import asyncio
import logging

from regex_engine.src.regex_engine.application.dto import ParsedIngredient
from regex_engine.src.regex_engine.domain.enums import RegexKind
from regex_engine.src.regex_engine.domain.errors import NameNotDetectedError
from regex_engine.src.regex_engine.domain.models.orchestrator import EnsureIngredientResult, EnsureWordResult
from regex_engine.src.regex_engine.ports.regex_registry import RegexRegistryRepository
from regex_engine.src.regex_engine.ports.regex_service import RegexService


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
    ("name", RegexKind.INGREDIENT_NAME),
)

class RegexOrchestratorDefault:
    def __init__(
            self,
            ingredient_names: RegexService,
            ingredient_conditions: RegexService,
            unit_sizes: RegexService,
            units: RegexService,
            repository: RegexRegistryRepository
    ):
        self._services: dict[RegexKind, RegexService] = {
            RegexKind.UNIT_SIZE: unit_sizes,
            RegexKind.UNIT: units,
            RegexKind.INGREDIENT_CONDITION: ingredient_conditions,
            RegexKind.INGREDIENT_NAME: ingredient_names
        }
        self.repository = repository

    async def save(self):
        for kind, service in self._services.items():
            registry = service.registry
            await self.repository.save(kind,registry)

    async def load(self):
        for kind, service in self._services.items():
            registry = await self.repository.load(kind)
            service.registry=registry


    async def ensure_ingredient_included_in_registry(self, ingredient: ParsedIngredient) -> EnsureIngredientResult:
        plan = _build_ensure_plan(ingredient)

        results = await asyncio.gather(
            *(self._services[kind].ensure_word_included_in_registry(value) for kind, value in plan.items()),
        )

        _log_ensure_items(results, context=ingredient.raw_input)

        return _build_ensure_output(results, ingredient.raw_input)


    async def _ensure_word_included_in_registry(self, kind: RegexKind, value: str) -> EnsureWordResult:
        return await self._services[kind].ensure_word_included_in_registry(value)
