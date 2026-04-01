import asyncio
import logging

from regex_engine.application.dto import ParsedIngredient
from regex_engine.application.use_cases.ingredient_regex_service import IngredientRegexService
from regex_engine.domain.enums import RegexKind
from regex_engine.domain.errors import NameNotDetectedError
from regex_engine.domain.models.orchestrator import EnsureIngredientResult, EnsureWordResult
from regex_engine.ports.regex_registry import RegexRegistryRepository, IngredientRegexRegistryRepository
from regex_engine.ports.regex_service import RegexService


logger = logging.getLogger("regex_orchestrator")


def _build_ensure_output(ensure_results: list[EnsureWordResult], raw_input: str) -> EnsureIngredientResult:
    by_kind = {r.kind: r for r in ensure_results}
    name = by_kind[RegexKind.INGREDIENT_NAME]

    return EnsureIngredientResult(raw_input=raw_input, name=name, items=by_kind)


def _log_ensure_items(items: list[EnsureWordResult], *, context: str) -> None:
    for item in items:
        status, stem = item.status, item.stem

        logger.info("[%s] %s=%s -> %s (stem: %s)",
                    context, item.kind, item.word, status.name, stem
                    )


def _build_ensure_plan(ingredient: ParsedIngredient) -> dict[RegexKind, str]:
    if not ingredient.name:
        raise NameNotDetectedError(ingredient=ingredient.raw_input)

    plan = {}
    for field, kind in FIELD_TO_KIND:
        value = getattr(ingredient, field)
        if value:
            plan[kind] = value

    return plan

FIELD_TO_KIND = (
    ("unit_size", RegexKind.UNIT_SIZE),
    ("unit", RegexKind.UNIT),
    ("condition", RegexKind.INGREDIENT_CONDITION),
)

class RegexOrchestratorDefault:
    def __init__(
            self,
            ingredient_names: IngredientRegexService,
            ingredient_conditions: RegexService,
            unit_sizes: RegexService,
            units: RegexService,
            repository: RegexRegistryRepository,
            ingredient_repository: IngredientRegexRegistryRepository
    ):
        self._services: dict[RegexKind, RegexService] = {
            RegexKind.UNIT_SIZE: unit_sizes,
            RegexKind.UNIT: units,
            RegexKind.INGREDIENT_CONDITION: ingredient_conditions,
        }
        self._ingredient_names = ingredient_names
        self._repository = repository
        self._ingredient_repository = ingredient_repository


    async def save(self):
        await self._ingredient_repository.save(self._ingredient_names.registry)

        for kind, service in self._services.items():
            registry = service.registry
            await self._repository.save(kind,registry)

    async def load(self):
        self._ingredient_names.registry = await self._ingredient_repository.load()

        for kind, service in self._services.items():
            registry = await self._repository.load(kind)
            service.registry=registry


    async def ensure_ingredient_included_in_registry(self, ingredient: ParsedIngredient) -> EnsureIngredientResult:
        plan = _build_ensure_plan(ingredient)

        ensure_result = await self._ingredient_names.ensure_word_included_in_registry(ingredient.name)

        results = await asyncio.gather(
            *(self._services[kind].ensure_word_included_in_registry(value) for kind, value in plan.items()),
        )

        results.append(ensure_result)

        _log_ensure_items(results, context=ingredient.raw_input)

        return _build_ensure_output(results, ingredient.raw_input)


    async def _ensure_word_included_in_registry(self, kind: RegexKind, value: str) -> EnsureWordResult:
        return await self._services[kind].ensure_word_included_in_registry(value)
