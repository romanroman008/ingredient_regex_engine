from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from regex_engine.adapters.categorizer.categorizer_service_default import CategorizerServiceDefault
from regex_engine.domain.enums import Category
from regex_engine.domain.errors import CategorizingError
from regex_engine.domain.models.categorized_ingredient import CategorizedIngredient
from regex_engine.ports.categories_repository import CategoryRepository
from regex_engine.ports.categorizer import Categorizer
from regex_engine.ports.regex_registry import RegexRegistryReader


def create_ingredient(stem: str):
    return SimpleNamespace(stem=stem)


def create_categorized_ingredient(
    stem: str,
    category: Category,
) -> CategorizedIngredient:
    return CategorizedIngredient(
        id=uuid4(),
        stem=stem,
        category=category,
    )


def create_registry_mock(*stems: str):
    registry = Mock(spec=RegexRegistryReader)
    registry.get_all.return_value = [create_ingredient(stem) for stem in stems]
    return registry


def create_categorizer_mock():
    categorizer = Mock(spec=Categorizer)
    categorizer.categorize = AsyncMock()
    return categorizer


def create_repository_mock(
    categorized_ingredients: dict[str, CategorizedIngredient] | None = None,
):
    repository = Mock(spec=CategoryRepository)
    repository.load.return_value = (
        categorized_ingredients
        if categorized_ingredients is not None
        else {}
    )
    return repository


def create_service(
    *,
    categorizer=None,
    repository=None,
):
    return CategorizerServiceDefault(
        categorizer=categorizer or create_categorizer_mock(),
        repository=repository or create_repository_mock(),
    )


@pytest.mark.asyncio
async def test_categorize__new_ingredient__adds_category():
    # Arrange
    categorizer = create_categorizer_mock()
    categorizer.categorize.return_value = Category.DAIRY

    repository = create_repository_mock()
    service = create_service(
        categorizer=categorizer,
        repository=repository,
    )
    registry = create_registry_mock("masło")

    # Act
    result = await service.categorize(registry)

    # Assert
    categorized = result["masło"]

    assert categorized.stem == "masło"
    assert categorized.category == Category.DAIRY
    repository.load.assert_called_once_with()
    categorizer.categorize.assert_awaited_once_with("masło")


@pytest.mark.asyncio
async def test_categorize__already_categorized_ingredient__does_not_call_categorizer():
    # Arrange
    categorizer = create_categorizer_mock()

    existing = create_categorized_ingredient(
        stem="masło",
        category=Category.DAIRY,
    )

    repository = create_repository_mock({"masło": existing})
    service = create_service(
        categorizer=categorizer,
        repository=repository,
    )
    registry = create_registry_mock("masło")

    # Act
    result = await service.categorize(registry)

    # Assert
    categorized = result["masło"]

    assert categorized.stem == "masło"
    assert categorized.category == Category.DAIRY
    repository.load.assert_called_once_with()
    categorizer.categorize.assert_not_awaited()


@pytest.mark.asyncio
async def test_categorize__unknown_existing_category__recategorizes_ingredient():
    # Arrange
    categorizer = create_categorizer_mock()
    categorizer.categorize.return_value = Category.DAIRY

    existing = create_categorized_ingredient(
        stem="masło",
        category=Category.UNKNOWN,
    )

    repository = create_repository_mock({"masło": existing})
    service = create_service(
        categorizer=categorizer,
        repository=repository,
    )
    registry = create_registry_mock("masło")

    # Act
    result = await service.categorize(registry)

    # Assert
    categorized = result["masło"]

    assert categorized.stem == "masło"
    assert categorized.category == Category.DAIRY
    repository.load.assert_called_once_with()
    categorizer.categorize.assert_awaited_once_with("masło")


@pytest.mark.asyncio
async def test_categorize__categorizer_error__skips_ingredient():
    # Arrange
    categorizer = create_categorizer_mock()
    categorizer.categorize.side_effect = CategorizingError("strwe", [])

    repository = create_repository_mock()
    service = create_service(
        categorizer=categorizer,
        repository=repository,
    )
    registry = create_registry_mock("strwe")

    # Act
    result = await service.categorize(registry)

    # Assert
    assert "strwe" not in result
    repository.load.assert_called_once_with()
    categorizer.categorize.assert_awaited_once_with("strwe")


def test_save__saves_categorized_ingredients_loaded_from_repository():
    # Arrange
    categorized_ingredients = {
        "masło": create_categorized_ingredient(
            stem="masło",
            category=Category.DAIRY,
        )
    }
    repository = create_repository_mock(categorized_ingredients)

    service = create_service(repository=repository)

    # Act
    service.save()

    # Assert
    repository.load.assert_called_once_with()
    repository.save.assert_called_once_with(categorized_ingredients)
