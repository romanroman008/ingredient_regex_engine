import json
import logging
import re
from collections import defaultdict
from pathlib import Path
from typing import Iterable
from collections.abc import Mapping
from typing import Any
from uuid import UUID
from regex_engine.domain.enums import Category
from regex_engine.domain.models.categorized_ingredient import CategorizedIngredient
from regex_engine.ports.categories_repository import CategoryRepository

logger = logging.getLogger(__name__)

VALID_WORD_RE = re.compile(r"^[\w\sąćęłńóśźżĄĆĘŁŃÓŚŹŻ-]+$")


def is_valid_word(value: str) -> bool:
    if not value or not value.strip():
        return False

    if not any(c.isalpha() for c in value):
        return False

    return bool(VALID_WORD_RE.fullmatch(value))




def _categorized_ingredient_from_payload(
    payload: Mapping[str, Any],
    *,
    expected_category: Category,
) -> CategorizedIngredient:
    raw_id = payload.get("id")
    raw_stem = payload.get("stem")
    raw_category = payload.get("category")

    if not isinstance(raw_id, str):
        raise TypeError("Expected ingredient id to be a string")

    if not isinstance(raw_stem, str):
        raise TypeError("Expected ingredient stem to be a string")

    if not is_valid_word(raw_stem):
        raise ValueError(f"Invalid ingredient stem: {raw_stem!r}")

    category = Category(raw_category)

    if category != expected_category:
        raise ValueError(
            f"Inconsistent category: outer={expected_category.value!r}, "
            f"inner={category.value!r}"
        )

    return CategorizedIngredient(
        id=UUID(raw_id),
        stem=raw_stem,
        category=category,
    )

def _load(payload: dict[str, list]) -> dict[str, CategorizedIngredient]:
    if not isinstance(payload, dict):
        raise TypeError("Expected payload to be a dict")

    result = {}

    for raw_category, ingredients in payload.items():
        try:
            category = Category(raw_category)
        except (ValueError, TypeError):
            logger.exception(f"Failed to parse category {raw_category}. Skipping.")
            continue

        if not isinstance(ingredients, Iterable) or isinstance(ingredients, (str, bytes)):
            logger.warning(f"Invalid ingredients for {raw_category}. Skipping.")
            continue

        for ingredient_payload in ingredients:
            try:
                ingredient_id = ingredient_payload.get("id")
                stem = ingredient_payload.get("stem")

                if not is_valid_word(stem):
                    raise TypeError(f"Invalid ingredient {stem}. Skipping.")
                result[stem] = CategorizedIngredient(id=UUID(ingredient_id), stem=stem, category=category)

            except (TypeError, AttributeError, ValueError):
                logger.warning("Failed to parse ingredient %s in %s", ingredient_payload, raw_category)
                continue
    return result




def _categorized_ingredients_to_payload(
        ingredients:dict[str, CategorizedIngredient]
):
    by_category:dict[Category:CategorizedIngredient] = defaultdict(list)

    for ingredient in ingredients.values():
        by_category[ingredient.category].append(ingredient)

    payload = {
        category.value: [
                {
                "id": str(ingredient.id),
                "stem": ingredient.stem,
                }
                for ingredient in by_category[category]
            ]
            for category in by_category
        }

    return payload


class FileCategoryRepository(CategoryRepository):
    def __init__(self, output_dir: Path):
        self._path = (output_dir / "categorized_ingredients").with_suffix(".json")

    def save(self, categorized_ingredients: dict[str, CategorizedIngredient]) -> None:

        payload = _categorized_ingredients_to_payload(categorized_ingredients)

        try:
            with self._path.open(mode="w", encoding="utf-8") as file:
                json.dump(payload, file, ensure_ascii=False, indent=2)
        except OSError:
            logger.exception("Failed to save categorized ingredients to: %s", self._path)
            raise

        logger.info(
            "Saved categorized %s ingredients to: %s", len(categorized_ingredients), self._path
        )

    def load(self) -> dict[str, CategorizedIngredient]:
        logger.info("Loading categories ...")

        if not self._path.exists():
            logger.info("No categories found at %s", self._path)
            return {}

        try:
            content = self._path.read_text(encoding="utf-8")
            if not content.strip():
                logger.info("No categories found at %s", self._path)
                return {}

            payload = json.loads(content)
        except json.JSONDecodeError as e:
            logger.exception("Invalid JSON in %s: %s. Returning empty categories", self._path, e)
            return {}
        except OSError as e:
            logger.exception("Failed to read %s: %s. Returning empty categories", self._path, e)
            return {}

        return _load(payload)
