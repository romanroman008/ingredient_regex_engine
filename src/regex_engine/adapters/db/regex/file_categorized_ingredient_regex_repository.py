import json
import logging
from collections import defaultdict
from pathlib import Path
from typing import Optional, Sequence
import re
from regex_engine.domain.enums import RegexKind, Category
from regex_engine.domain.models.regex_entry import RegexEntry
from regex_engine.domain.models.regex_registry import RegexRegistry
from regex_engine.ports.regex_registry import RegexRegistryReader
from settings import OUTPUT_DIR

logger = logging.getLogger(__name__)


def _create_payload(entries: Sequence[RegexEntry]) -> list[dict]:
    return [
            {
                "stem": entry.stem,
                "variants": sorted(entry.variants),
                "pattern": entry.pattern.pattern
            }
            for entry in entries
        ]


def _load_payload(payload:list[dict]) -> list[RegexEntry]:
    if not isinstance(payload, list):
        raise ValueError("Expected payload to be a list")

    entries = []
    for entry in payload:
        try:
            regex_entry = RegexEntry(
                stem=entry["stem"],
                variants=set(entry["variants"])
            )
            entries.append(regex_entry)
        except (ValueError, TypeError, re.error) as e:
            logger.warning(
                "Invalid regex entry. Skipping ...",
                extra={
                    "stem": entry["stem"],
                    "variants": entry["variants"],
                    "error": str(e),
                }
            )
            continue

    return entries


def _load_categorized_payload(payload:dict[Category, list[dict]]):
    if not isinstance(payload, dict):
        raise ValueError("Expected categorized payload to be a dict")

    result = []
    for entries in payload.values():
        for entry in entries:
            try:
                regex_entry = RegexEntry(
                    stem=entry["stem"],
                    variants=entry["variants"],
                )
                result.append(regex_entry)
            except (ValueError, TypeError, re.error) as e:
                logger.warning(
                    "Invalid regex entry. Skipping ...",
                    extra={
                        "stem": entry["stem"],
                        "variants": entry["variants"],
                        "error": str(e),
                    }
                )
                continue

    return result


class FileCategorizedIngredientRegexRepository:
    path: Path = OUTPUT_DIR / "regexes"

    def __init__(self, categorized_stems:dict[str, Category], path: Path | None = None) -> None:
        self._path = path or OUTPUT_DIR / "regexes"
        self._categorized_stems:dict[str, Category] = categorized_stems

    def save(self, registry: RegexRegistryReader) -> None:
        kind = registry.kind
        logger.info(f"Saving regexes: %s ...", kind.name)
        entries = registry.get_all()

        if kind == RegexKind.INGREDIENT_NAME:
            payload = self._create_categorized_payload(entries)
        else:
            payload = _create_payload(entries)

        path = self._create_path(kind)

        try:
            with path.open("w", encoding="utf-8") as file:
                json.dump(payload, file, ensure_ascii=False, indent=2)
        except OSError as e:
            logger.exception("Failed to save regexes to %s: %s", path, e)
            raise

        logger.info("Saved %s regexes to: .", len(entries), path)


    def load(self, kind:RegexKind) -> RegexRegistry:
        logger.info(f"Loading regexes: %s ...", kind.name)
        path = self._create_path(kind)

        if not path.exists():
            logger.info(f"No regexes found at {path}")
            return RegexRegistry(kind, [])

        try:
            with path.open("r", encoding="utf-8") as file:
                raw = json.load(file)
        except json.JSONDecodeError as e:
            logger.exception("Invalid JSON in %s: %s", path, e)
            return RegexRegistry(kind, [])
        except OSError as e:
            logger.exception("Failed to read %s: %s", path, e)
            return RegexRegistry(kind, [])

        try:
            if kind == RegexKind.INGREDIENT_NAME:
                entries = _load_categorized_payload(raw)
            else:
                entries = _load_payload(raw)
        except ValueError as e:
            logger.exception("Invalid payload structure in %s: %s", path, e)
            return RegexRegistry(kind, [])


        logger.info(f"Loaded %s regexes.", len(entries))
        return RegexRegistry(kind, entries)




    def _create_categorized_payload(self, entries:Sequence[RegexEntry]) -> dict[Category, list[dict]]:
        payload = defaultdict(list)

        for entry in entries:
            category = self._categorized_stems.get(entry.stem)
            if not category:
                category = Category.UNKNOWN

            payload[category.value].append({
                "stem":entry.stem,
                "variants": sorted(entry.variants),
                "pattern": entry.pattern.pattern,
            })

        return payload

    def _create_path(self, kind: RegexKind) -> Path:
        name = kind.name.lower()
        path = (self._path / name).with_suffix(".json")
        path.parent.mkdir(parents=True, exist_ok=True)
        return path


    def update_categories(self, categorized_stems: dict[str, Category]) -> None:
        for stem, category in categorized_stems.items():
            self._categorized_stems[stem] = category