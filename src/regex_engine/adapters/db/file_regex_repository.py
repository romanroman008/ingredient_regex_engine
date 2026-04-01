import json
import logging
import re
from pathlib import Path

from settings import OUTPUT_DIR
from regex_engine.domain.enums import RegexKind
from regex_engine.domain.models.regex_entry import RegexEntry
from regex_engine.domain.models.regex_registry import RegexRegistry

logger = logging.getLogger("regex_repository")



class FileRegexRepository:
    path = OUTPUT_DIR / "regexes"

    async def save(self, kind:RegexKind, registry: RegexRegistry) -> None:
        logger.info(f"Saving regexes: %s ...", kind.name)
        entries = registry.get_all()
        payload = [
            {
                "stem":entry.stem,
                "variants":entry.variants,
                "pattern": entry.pattern
            }
            for entry in entries
        ]
        path = self._create_path(kind)
        with path.open("w", encoding="utf-8") as file:
            json.dump(payload, file, ensure_ascii=False, indent=2)
        logger.info("Saved %s regexes to: .", len(entries), path)

    async def load(self, kind:RegexKind) -> RegexRegistry:
        logger.info(f"Loading regexes: %s ...", kind.name)
        path = self._create_path(kind)

        if not path.exists():
            logger.info(f"No regexes found at {path}")
            return RegexRegistry([])

        entries = []
        with path.open("r", encoding="utf-8") as file:
            raw = json.load(file)

            for item in raw:
                try:
                    regex_entry = RegexEntry(
                        stem=item["stem"],
                        variants=set(item["variants"])
                    )
                    entries.append(regex_entry)
                except (ValueError, TypeError, re.error) as e:
                    logger.warning(
                        "Invalid regex entry. Skipping ...",
                        extra={
                            "stem": item["stem"],
                            "variants": item["variants"],
                            "error": str(e),
                        }
                    )
                    continue

        logger.info(f"Loaded %s regexes.", len(entries))
        return RegexRegistry(entries)





    def _create_path(self, kind:RegexKind) -> Path:
        name = kind.name.lower()
        path = self.path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        return path