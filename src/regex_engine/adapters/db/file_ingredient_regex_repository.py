import json
import logging
import re
from pathlib import Path


from regex_engine.domain.models.ingredient_entry import IngredientEntry
from regex_engine.domain.models.ingredient_regex_registry import IngredientRegexRegistry
from regex_engine.ports.regex_registry import IngredientRegexRegistryRepository
from settings import OUTPUT_DIR
from regex_engine.domain.enums import Category

logger = logging.getLogger("ingredient_regex_reposity")



class FileIngredientRegexRepository(IngredientRegexRegistryRepository):
    path = OUTPUT_DIR / "regexes"

    async def save(self, registry: IngredientRegexRegistry) -> None:
        logger.info(f"Saving ingredients names regexes ...")
        entries = registry.get_all()

        payload = {}

        for category, entries in registry.get_all_by_category():
            payload = {
                "category": category.value,
                "ingredients": [
                    {
                        "stem": entry.stem,
                        "variants": entry.variants,
                        "pattern": entry.pattern,
                    }
                    for entry in entries
                ]
            }

        path = self._create_path()
        with path.open("w", encoding="utf-8") as file:
            json.dump(payload, file, ensure_ascii=False, indent=2)
        logger.info("Saved %s regexes to: .", len(entries), path)

    async def load(self) -> IngredientRegexRegistry:
        logger.info(f"Loading ingredients names regexes ...")
        path = self._create_path()

        if not path.exists():
            logger.info(f"No regexes found at {path}")
            return IngredientRegexRegistry([])

        entries = []
        with path.open("r", encoding="utf-8") as file:
            raw = json.load(file)

            for item in raw:
                try:
                    regex_entry = IngredientEntry(
                        stem=item["stem"],
                        variants=set(item["variants"]),
                        category=Category(item["category"]),
                    )
                    entries.append(regex_entry)

                except (ValueError, TypeError, re.error) as e:
                    logger.warning(
                        "Invalid regex entry. Skipping ...",
                        extra={
                            "stem": item["stem"],
                            "variants": item["variants"],
                            "category": item["category"],
                            "error": str(e),
                        }
                    )
                    continue

        logger.info(f"Loaded %s regexes.", len(entries))
        return IngredientRegexRegistry(entries)





    def _create_path(self, file_name:str = "ingredient_name") -> Path:
        path = self.path / file_name
        path.parent.mkdir(parents=True, exist_ok=True)
        return path