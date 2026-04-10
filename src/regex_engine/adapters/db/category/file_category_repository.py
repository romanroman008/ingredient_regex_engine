import json
import logging
import re
from collections import defaultdict
from pathlib import Path
from typing import Iterable

from regex_engine.domain.enums import Category
from settings import OUTPUT_DIR

logger = logging.getLogger(__name__)

VALID_WORD_RE = re.compile(r"^[\w\sąćęłńóśźżĄĆĘŁŃÓŚŹŻ-]+$")

def is_valid_word(value: str) -> bool:
    if not value or not value.strip():
        return False

    if not any(c.isalpha() for c in value):
        return False

    return bool(VALID_WORD_RE.fullmatch(value))

def _load(payload:dict[str, list]) -> dict[str, Category]:
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

        for ingredient in ingredients:
            try:
                if not is_valid_word(ingredient):
                    raise TypeError(f"Invalid ingredient {ingredient}. Skipping.")
                result[ingredient] = category
            except (TypeError, AttributeError):
                logger.warning("Failed to parse ingredient %s in %s", ingredient, raw_category)
                continue
    return result


class FileCategoryRepository:
    def __init__(self, path: Path | None = None):
        self._path = path or (OUTPUT_DIR / "categorized_ingredients").with_suffix(".json")


    def save(self, categorized_ingredients:dict[str, Category]):
        payload = defaultdict(list)

        for stem, category in categorized_ingredients.items():
            payload[category.value].append(stem)

        try:
            with self._path.open(mode="w", encoding="utf-8") as file:
                json.dump(payload, file, ensure_ascii=False, indent=2)
        except OSError:
            logger.exception("Failed to save categorized ingredients to: %s", self._path)
            raise

        logger.info("Saved categorized %s ingredients to: %s",
                    len(categorized_ingredients),
                    self._path)



    def load(self):
        logger.info("Loading categories ...")

        if not self._path.exists():
            logger.info(f"No regexes found at {self._path}")
            return {}

        try:
            with self._path.open("r", encoding="utf-8") as file:
                payload = json.load(file)
        except json.JSONDecodeError as e:
            logger.exception("Invalid JSON in %s: %s", self._path, e)
            return {}
        except OSError as e:
            logger.exception("Failed to read %s: %s", self._path, e)
            return {}


        return _load(payload)


