import logging


from regex_engine.application.dto.agent.parsed_ingredient import ParsedIngredient
from regex_engine.domain.enums import RegexKind
from regex_engine.domain.errors import ReducingRecordsError, RecordSelectionError, IngredientParsingError, \
    EveryRecordIterated

from regex_engine.domain.models.ingredient_record import IngredientRecord
from regex_engine.domain.models.orchestrator import EnsureIngredientResult
from regex_engine.domain.models.resolved_ingredient import ResolvedIngredient

from regex_engine.ports.ingredient_parser import IngredientParser
from regex_engine.ports.regex_orchestrator import RegexOrchestrator

from regex_engine.ports.regex_resolver import RegexResolver

logger = logging.getLogger("regex_engine")

def build_failed_resolved_ingredient(
    issue: Exception,
    raw_input: str = "",
) -> ResolvedIngredient:
    return ResolvedIngredient(
        raw_input=raw_input,
        issues=[issue],
    )

def build_resolved_ingredient(ingredient:ParsedIngredient,
                              ensure_result:EnsureIngredientResult,
                              ) -> ResolvedIngredient:
    issues = []

    for word_result in ensure_result.items.values():
        if word_result.exception:
            issues.append(word_result.exception)

    if ensure_result.name.exception:
        issues.append(ensure_result.name.exception)

    return ResolvedIngredient(
        raw_input=ingredient.raw_input,
        amount=ingredient.amount,
        unit_size=ensure_result.items.get(RegexKind.UNIT_SIZE),
        unit=ensure_result.items.get(RegexKind.UNIT),
        condition=ensure_result.items.get(RegexKind.INGREDIENT_CONDITION),
        name=ensure_result.name,
        extra=ingredient.extra,
        issues=issues
    )


class IngredientFilterEngine:
    def __init__(self,
                 regex_orchestrator: RegexOrchestrator,
                 regex_resolver: RegexResolver,
                 parser: IngredientParser,
                 ):
        self.regex_orchestrator = regex_orchestrator
        self.regex_resolver = regex_resolver
        self.parser = parser

    @staticmethod
    def _sort_by_count_desc(records: list[IngredientRecord]) -> list[IngredientRecord]:
        return sorted(records, key=lambda r: r.count, reverse=True)

    def filter_records_with_conj(self, records: list[IngredientRecord]) -> list[IngredientRecord]:
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
            try:
                if self.regex_resolver.can_be_standardized(record.name):
                    continue
            except Exception as e:
                raise ReducingRecordsError(
                    f"Error occurred while trying to standardise {record.name}: {e}",
                    record=record,
                ) from e
            remaining.append(record)

        logger.info(f"Reduced %s records", len(records) - len(remaining))
        logger.info(f"Remaining {len(remaining)} records")

        return remaining

    def get_first_non_iterated_record(
            self,
            records: list[IngredientRecord],
    ) -> IngredientRecord:
        not_iterated = [
            record
            for record in records
            if not record.iterated
        ]

        if not not_iterated:
            raise EveryRecordIterated(
                "No non-iterated records available",
            )

        try:

            return self._sort_by_count_desc(not_iterated)[0]
        except Exception as e:
            raise RecordSelectionError(
                "Failed to select record with highest count",
                records_count=len(not_iterated),
            ) from e



    async def filter_records(self, ingredients: list[IngredientRecord], max_rounds: int = 10) -> list[ResolvedIngredient]:
        logger.info("Filtering records with conjunction ...")
        records_left = self.filter_records_with_conj(ingredients)
        records_left = self._sort_by_count_desc(records_left)

        result = []
        success = 0
        failed = 0

        for i in range(max_rounds):
            try:
                logger.info(f"Iteration %s of %s ...", i + 1, max_rounds)

                records_left = self.reduce_records(records_left)

                ingredient = self.get_first_non_iterated_record(records_left)

                ingredient.iterated = True

                parsed_ingredient = await self.parser.parse(ingredient.name)

                ensure_result = await self.regex_orchestrator.ensure_ingredient_included_in_registry(parsed_ingredient)

                resolved_ingredient = build_resolved_ingredient(ingredient=parsed_ingredient, ensure_result=ensure_result)
                result.append(resolved_ingredient)

                if resolved_ingredient.issues:
                    logger.warning("Issues occurred in iteration %s/%s", i, max_rounds)
                    logger.warning(resolved_ingredient.issues)
                    failed += 1

                else:
                    logger.info("Iteration %s/%s completed successfully", i, max_rounds)
                    success += 1

            except EveryRecordIterated:
                break

            except (RecordSelectionError, ReducingRecordsError) as e:
                logger.exception("Error in iteration %s: %s", i + 1, e)
                result.append(build_failed_resolved_ingredient(e))
                failed += 1
                continue

            except IngredientParsingError as e:
                logger.error(
                    "Ingredient parsing failed",
                    extra={
                        "ingredient": e.ingredient,
                        "failures": [
                            {
                                "attempt": f.attempt,
                                "error_type": type(f.cause).__name__,
                                "error": str(f.cause),
                            }
                            for f in e.failures
                        ],
                    },
                    exc_info=True,
                )
                failed += 1
                continue

            except Exception as e:
                logger.exception("Error in iteration %s: %s", i + 1, e)
                result.append(build_failed_resolved_ingredient(raw_input=ingredient.name, issue=e))
                failed += 1
                continue

        logger.info(f"Finished filtering records {max_rounds}. Success: {success}, Failed: {failed}")
        return result





