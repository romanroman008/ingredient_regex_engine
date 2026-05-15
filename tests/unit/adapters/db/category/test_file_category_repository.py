import json
from uuid import NAMESPACE_URL, UUID, uuid5

import pytest

from regex_engine.adapters.db.file.category.file_category_repository import FileCategoryRepository
from regex_engine.domain.enums import Category
from regex_engine.domain.models.categorized_ingredient import CategorizedIngredient


@pytest.fixture
def repository(tmp_path):
    full_path = tmp_path
    return FileCategoryRepository(full_path)


def ingredient_id(stem: str) -> UUID:
    return uuid5(NAMESPACE_URL, f"regex-engine:test:ingredient:{stem}")


def ingredient(stem: str, category: Category) -> CategorizedIngredient:
    return CategorizedIngredient(
        id=ingredient_id(stem),
        stem=stem,
        category=category,
    )


def ingredients_by_stem(*items: tuple[str, Category]) -> dict[str, CategorizedIngredient]:
    return {stem: ingredient(stem, category) for stem, category in items}


def ingredient_payload(stem: str) -> dict[str, str]:
    return {
        "id": str(ingredient_id(stem)),
        "stem": stem,
    }


def write_payload(repository: FileCategoryRepository, payload: object) -> None:
    repository._path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


@pytest.mark.parametrize(
    "categorized_ingredients, expected_json",
    [
        pytest.param(
            ingredients_by_stem(
                ("jabłko", Category.FRUITS),
                ("sezam", Category.NUTS_AND_SEEDS),
                ("jajka", Category.EGGS),
                ("maliny", Category.FRUITS),
                ("kakao", Category.NUTS_AND_SEEDS),
            ),
            {
                "owoce": [ingredient_payload("jabłko"), ingredient_payload("maliny")],
                "orzechy i nasiona": [ingredient_payload("sezam"), ingredient_payload("kakao")],
                "jajka": [ingredient_payload("jajka")],
            },
            id="multiple_categories",
        ),
        pytest.param(
            ingredients_by_stem(
                ("jabłko", Category.FRUITS),
                ("sezam", Category.NUTS_AND_SEEDS),
                ("jajka", Category.EGGS),
            ),
            {
                "owoce": [ingredient_payload("jabłko")],
                "orzechy i nasiona": [ingredient_payload("sezam")],
                "jajka": [ingredient_payload("jajka")],
            },
            id="single_categories",
        ),
        pytest.param(
            {},
            {},
            id="empty",
        ),
    ],
)
def test_save__happy_path(repository, categorized_ingredients, expected_json):
    # Act
    repository.save(categorized_ingredients)

    # Assert
    with repository._path.open(encoding="utf-8") as f:
        actual = json.load(f)

    assert actual == expected_json


@pytest.mark.parametrize(
    "payload, expected",
    [
        pytest.param(
            {
                "owoce": [ingredient_payload("jabłko"), ingredient_payload("maliny")],
                "orzechy i nasiona": [ingredient_payload("sezam"), ingredient_payload("kakao")],
                "jajka": [ingredient_payload("jajka")],
            },
            ingredients_by_stem(
                ("jabłko", Category.FRUITS),
                ("sezam", Category.NUTS_AND_SEEDS),
                ("jajka", Category.EGGS),
                ("maliny", Category.FRUITS),
                ("kakao", Category.NUTS_AND_SEEDS),
            ),
            id="multiple_categories",
        ),
        pytest.param(
            {
                "owoce": [ingredient_payload("jabłko")],
                "orzechy i nasiona": [ingredient_payload("sezam")],
                "jajka": [ingredient_payload("jajka")],
            },
            ingredients_by_stem(
                ("jabłko", Category.FRUITS),
                ("sezam", Category.NUTS_AND_SEEDS),
                ("jajka", Category.EGGS),
            ),
            id="single_categories",
        ),
        pytest.param(
            {
                "owoce": [1, ingredient_payload("maliny")],
                "orzechy i nasiona": [ingredient_payload("sezam"), ingredient_payload("kakao")],
                "jajka": [],
                "rośliny strączkowe": [ingredient_payload("fasola")],
            },
            ingredients_by_stem(
                ("maliny", Category.FRUITS),
                ("sezam", Category.NUTS_AND_SEEDS),
                ("kakao", Category.NUTS_AND_SEEDS),
                ("fasola", Category.LEGUMES),
            ),
            id="some_invalid_elements",
        ),
        pytest.param(
            {
                "owoce": [ingredient_payload("jabłko"), ingredient_payload("maliny")],
                "orzechy i nasiona": [ingredient_payload("sezam"), ingredient_payload("kakao")],
                "jajca": [ingredient_payload("jajka")],
                "rośliny": [ingredient_payload("fasola"), ingredient_payload("ciecierzyca")],
                "zupy/buliony": [ingredient_payload("zupa pomidorowa")],
            },
            ingredients_by_stem(
                ("jabłko", Category.FRUITS),
                ("maliny", Category.FRUITS),
                ("sezam", Category.NUTS_AND_SEEDS),
                ("kakao", Category.NUTS_AND_SEEDS),
                ("zupa pomidorowa", Category.SOUPS),
            ),
            id="some_invalid_categories",
        ),
        pytest.param(
            {
                "owoce": [
                    {"stem": "jabłko"},
                    {"id": "invalid-ingredient-id", "stem": "maliny"},
                ],
                "orzechy i nasiona": [ingredient_payload("sezam")],
            },
            ingredients_by_stem(("sezam", Category.NUTS_AND_SEEDS)),
            id="some_invalid_ids",
        ),
        pytest.param(
            {
                "owoce": [
                    {"id": str(ingredient_id("jabłko"))},
                    {"id": str(ingredient_id("maliny")), "stem": "!!!"},
                ],
                "orzechy i nasiona": [ingredient_payload("sezam")],
            },
            ingredients_by_stem(("sezam", Category.NUTS_AND_SEEDS)),
            id="some_invalid_stems",
        ),
        pytest.param(
            {
                "owoce": "jabłko",
                "orzechy i nasiona": [ingredient_payload("sezam")],
            },
            ingredients_by_stem(("sezam", Category.NUTS_AND_SEEDS)),
            id="invalid_category_payload_type",
        ),
    ],
)
def test_load__happy_path(repository, payload, expected):
    # Arrange
    write_payload(repository, payload)

    # Act
    actual = repository.load()

    # Assert
    assert actual == expected


@pytest.mark.parametrize(
    "content",
    [
        pytest.param("", id="empty_file"),
        pytest.param("   ", id="blank_file"),
        pytest.param("{invalid-json", id="invalid_json"),
    ],
)
def test_load__returns_empty_when_file_has_no_valid_payload(repository, content):
    # Arrange
    repository._path.write_text(content, encoding="utf-8")

    # Act
    actual = repository.load()

    # Assert
    assert actual == {}


def test_load__returns_empty_when_file_does_not_exist(repository):
    # Act
    actual = repository.load()

    # Assert
    assert actual == {}
