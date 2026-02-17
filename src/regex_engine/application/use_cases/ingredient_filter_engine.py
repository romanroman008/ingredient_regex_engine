
import json
import logging

from pathlib import Path


from regex_engine.src.regex_engine.domain.errors import NameNotDetectedError
from regex_engine.src.regex_engine.domain.models.ingredient_record import IngredientRecord
from regex_engine.src.regex_engine.ports.ingredient_parser import IngredientParser
from regex_engine.src.regex_engine.ports.regex_orchestrator import RegexOrchestrator
from regex_engine.src.regex_engine.ports.regex_resolver import RegexResolver

logger = logging.getLogger("regex_engine")


class IngredientFilterEngine:
    def __init__(self, regex_orchestrator: RegexOrchestrator, regex_resolver: RegexResolver, parser: IngredientParser):
        self.regex_orchestrator = regex_orchestrator
        self.regex_resolver = regex_resolver
        self.parser = parser

    @staticmethod
    def _sort_by_count_desc(records: list[IngredientRecord]) -> list[IngredientRecord]:
        return sorted(records, key=lambda r: r.count, reverse=True)


    @staticmethod
    def categorize(ingredient_stem: str):
        pass

    def filter_records_with_conj(self, records: list[IngredientRecord]):
        clean = []

        for ingredient in records:
            if not self.regex_resolver.contains_conjunction(ingredient.name):
                if not self.regex_resolver.and_conjunction_between_numbers(ingredient.name):
                    clean.append(ingredient)

        records_with_conj = len(records) - len(clean)
        logger.info("Found %s records with conjunction", records_with_conj)

        return clean

    def reduce_records(self, records: list[IngredientRecord]) -> list[IngredientRecord]:
        remaining = []


        for record in records:
            if self.regex_resolver.can_be_standardized(record.name):
                continue

            remaining.append(record)

        logger.info(f"Reduced %s records", len(records) - len(remaining))
        logger.info(f"Remaining {len(remaining)} records")

        return remaining

    def get_record_with_highest_count(self, records: list[IngredientRecord]) -> IngredientRecord:
        not_iterated = [
            record
            for record in records
            if not record.iterated
        ]
        sorted = self._sort_by_count_desc(not_iterated)
        return sorted[0]

    def save_iterated_raw_ingredient(self, ingredients: list[IngredientRecord]):
        logger.info("Saving raw ...")
        path = Path("regexes") / "raw_inputs.json"
        payload = [
            {
                "name": ingredient.name
            }
            for ingredient in ingredients
            if ingredient.iterated
        ]

        with path.open("w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)

    async def filter_records(self, ingredients: list[IngredientRecord], max_rounds: int = 10):
        total_records_number = len(ingredients)

        logger.info("Loading regexes ...")
        await self.regex_orchestrator.load()


        records_left = ingredients

        for i in range(max_rounds):

            logger.info(f"Iteration %s of %s ...", i+1, max_rounds)
            # Tu może się zapętlić, aczkolwiek 3 próby zapetlenia wynikałyby z ponownego podejscia do parsowania składnika
            records_left = self.reduce_records(records_left)

            ingredient = self.get_record_with_highest_count(records_left)

            parsed_ingredient = await self.parser.parse(ingredient.name)

            try:
                await self.regex_orchestrator.ensure_ingredient_included_in_registry(parsed_ingredient)

            except NameNotDetectedError:
                logger.warning(f"Could not detect name in {ingredient.name}")
                ingredient.attempts += 1
                if ingredient.attempts >= 3:
                    ingredient.iterated = True
                    logger.error("Giving up on ingredient: %s, attempts: %s", ingredient.name, ingredient.attempts)
                continue

            else:
                ingredient.iterated = True

        logger.info("Saving regexes ...")
        await self.regex_orchestrator.save()
        self.save_iterated_raw_ingredient(ingredients)
