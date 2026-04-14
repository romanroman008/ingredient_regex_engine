from unittest.mock import AsyncMock

import pytest
from envs.django.Lib.unittest.mock import create_autospec

from regex_engine.application.dto.agent.parsed_ingredient import ParsedIngredient
from regex_engine.application.use_cases.regex_orchestrator_default import RegexOrchestratorDefault
from regex_engine.domain.enums import RegexKind, EnsureStatus

from regex_engine.domain.errors import NameNotDetectedError
from regex_engine.domain.models.orchestrator import EnsureIngredientResult, EnsureWordResult


from regex_engine.ports.regex_registry import RegexRegistryRepository
from regex_engine.ports.regex_service import RegexService


def _mk_service():
    svc = create_autospec(RegexService, instance=True, spec_set=True)
    svc.ensure_word_included_in_registry = AsyncMock()
    svc.registry = create_autospec(RegexRegistry, instance=True, spec_set=True)
    return svc

def _make_parsed_ingredient(**overrides) -> ParsedIngredient:
    data = dict(
        raw_input="2 czubate łyżki gorzkiego kakao",
        amount=2.0,
        unit_size="czubate",
        unit="łyżki",
        condition="gorzkiego",
        name="kakao",

    )
    data.update(overrides)
    return ParsedIngredient(**data)



@pytest.fixture
def ingredient_names():
    return _mk_service()


@pytest.fixture
def ingredient_conditions():
    return _mk_service()


@pytest.fixture
def unit_sizes():
    return _mk_service()


@pytest.fixture
def units():
    return _mk_service()


@pytest.fixture
def repository():
    repo = create_autospec(RegexRegistryRepository, instance=True, spec_set=True)
    repo.save = AsyncMock()
    repo.load = AsyncMock()
    return repo


@pytest.fixture
def orchestrator(
    ingredient_names,
    ingredient_conditions,
    unit_sizes,
    units,
    repository,
):
    return RegexOrchestratorDefault(
        ingredient_names=ingredient_names,
        ingredient_conditions=ingredient_conditions,
        unit_sizes=unit_sizes,
        units=units,
        repository=repository,
    )

@pytest.mark.asyncio
async def test_save(orchestrator:RegexOrchestratorDefault):

    # Arrange
    orchestrator.repository.save = AsyncMock()

    # Act
    await orchestrator.save()

    # Assert
    assert orchestrator.repository.save.await_count == 4


@pytest.mark.asyncio
async def test_load(orchestrator:RegexOrchestratorDefault):

    # Arrange
    orchestrator.repository.load = AsyncMock()

    # Acto
    await orchestrator.load()

    # Assert
    assert orchestrator.repository.load.await_count == 4

@pytest.mark.parametrize(
    "overrides",
    [
        ({"unit_size": "czubate", "name":"",}),
        ({"unit_size": "","name":"", "unit":""}),
    ]
)
@pytest.mark.asyncio
async def test_ensure_ingredient_included_in_registry__no_name__raises(
        orchestrator:RegexOrchestratorDefault,
        overrides):

    # Arrange
    ingredient = _make_parsed_ingredient(**overrides)

    # Act / Assert
    with pytest.raises(NameNotDetectedError):
        await orchestrator.ensure_ingredient_included_in_registry(ingredient)

def _build_ensure_word_result(kind: RegexKind) -> EnsureWordResult:
    return EnsureWordResult(kind=kind, status=EnsureStatus.CREATED_NEW, stem="STEM", word="WORD")

@pytest.mark.asyncio
async def test_ensure_ingredient_included_in_registry__calls_all_services(orchestrator):
    ingredient = _make_parsed_ingredient(
        raw_input="2 czubate łyżki cukru trzcinowego",
        amount=2.0,
        unit_size="czubate",
        unit="łyżki",
        condition="trzcinowego",
        name="cukru",
    )

    orchestrator._services[RegexKind.UNIT_SIZE].ensure_word_included_in_registry.return_value = _build_ensure_word_result(RegexKind.UNIT_SIZE)
    orchestrator._services[RegexKind.UNIT].ensure_word_included_in_registry.return_value = _build_ensure_word_result(RegexKind.UNIT)
    orchestrator._services[RegexKind.INGREDIENT_CONDITION].ensure_word_included_in_registry.return_value = _build_ensure_word_result(RegexKind.INGREDIENT_CONDITION)
    orchestrator._services[RegexKind.INGREDIENT_NAME].ensure_word_included_in_registry.return_value = _build_ensure_word_result(RegexKind.INGREDIENT_NAME)

    await orchestrator.ensure_ingredient_included_in_registry(ingredient)

    orchestrator._services[RegexKind.UNIT_SIZE].ensure_word_included_in_registry.assert_awaited_once_with("czubate")
    orchestrator._services[RegexKind.UNIT].ensure_word_included_in_registry.assert_awaited_once_with("łyżki")
    orchestrator._services[RegexKind.INGREDIENT_CONDITION].ensure_word_included_in_registry.assert_awaited_once_with("trzcinowego")
    orchestrator._services[RegexKind.INGREDIENT_NAME].ensure_word_included_in_registry.assert_awaited_once_with("cukru")


@pytest.mark.asyncio
async def test_ensure_ingredient_included_in_registry__only_name(orchestrator):
    ingredient = _make_parsed_ingredient(
        raw_input="2 czubate łyżki cukru trzcinowego",
        amount=0,
        unit_size="",
        unit="",
        condition="",
        name="cukru",
    )


    orchestrator._services[RegexKind.INGREDIENT_NAME].ensure_word_included_in_registry.return_value = _build_ensure_word_result(RegexKind.INGREDIENT_NAME)

    await orchestrator.ensure_ingredient_included_in_registry(ingredient)

    orchestrator._services[RegexKind.UNIT_SIZE].ensure_word_included_in_registry.assert_not_awaited()
    orchestrator._services[RegexKind.UNIT].ensure_word_included_in_registry.assert_not_awaited()
    orchestrator._services[RegexKind.INGREDIENT_CONDITION].ensure_word_included_in_registry.assert_not_awaited()
    orchestrator._services[RegexKind.INGREDIENT_NAME].ensure_word_included_in_registry.assert_awaited_once_with("cukru")



import pytest

from regex_engine.domain.enums import RegexKind, EnsureStatus


@pytest.mark.asyncio
async def test_ensure_ingredient_included_in_registry__only_name__returns_ensure(orchestrator):
    # Arrange
    ingredient = _make_parsed_ingredient(
        raw_input="cukru",
        amount=0,
        unit_size="",
        unit="",
        condition="",
        name="cukru",
    )

    expected_name = _build_ensure_word_result(RegexKind.INGREDIENT_NAME)
    orchestrator._services[RegexKind.INGREDIENT_NAME].ensure_word_included_in_registry.return_value = expected_name

    # Act
    result = await orchestrator.ensure_ingredient_included_in_registry(ingredient)



    # Assert - output (EnsureIngredientResult)
    assert result.raw_input == ingredient.raw_input
    assert result.name == expected_name

    # items powinno zawierać wyłącznie NAME
    assert set(result.items.keys()) == {RegexKind.INGREDIENT_NAME}
    assert result.items[RegexKind.INGREDIENT_NAME] == expected_name



@pytest.mark.asyncio
async def test_ensure_ingredient_included_in_registry__every_field__returns_ensure(orchestrator):
    # Arrange
    ingredient = _make_parsed_ingredient(
        raw_input="2 czubate łyżki cukru trzcinowego",
        amount=2.0,
        unit_size="czubate",
        unit="łyżki",
        condition="trzcinowego",
        name="cukru",
    )

    expected_name = _build_ensure_word_result(RegexKind.INGREDIENT_NAME)
    expected_unit_size = _build_ensure_word_result(RegexKind.UNIT_SIZE)
    expected_unit = _build_ensure_word_result(RegexKind.UNIT)
    expected_condition = _build_ensure_word_result(RegexKind.INGREDIENT_CONDITION)

    orchestrator._services[RegexKind.INGREDIENT_NAME].ensure_word_included_in_registry.return_value = expected_name
    orchestrator._services[RegexKind.UNIT_SIZE].ensure_word_included_in_registry.return_value = expected_unit_size
    orchestrator._services[RegexKind.UNIT].ensure_word_included_in_registry.return_value = expected_unit
    orchestrator._services[RegexKind.INGREDIENT_CONDITION].ensure_word_included_in_registry.return_value = expected_condition

    # Act
    result = await orchestrator.ensure_ingredient_included_in_registry(ingredient)



    # Assert
    assert result.raw_input == ingredient.raw_input
    assert result.name == expected_name


    assert set(result.items.keys()) == {RegexKind.INGREDIENT_NAME, RegexKind.UNIT_SIZE, RegexKind.UNIT, RegexKind.INGREDIENT_CONDITION}
    assert result.items[RegexKind.INGREDIENT_NAME] == expected_name
    assert result.items[RegexKind.INGREDIENT_CONDITION] == expected_condition
    assert result.items[RegexKind.UNIT_SIZE] == expected_unit_size
    assert result.items[RegexKind.UNIT] == expected_unit










