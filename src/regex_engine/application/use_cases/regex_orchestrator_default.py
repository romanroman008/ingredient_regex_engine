import asyncio
import logging

from regex_engine.src.regex_engine.adapters.models import ParsedIngredient
from regex_engine.src.regex_engine.domain.enums import RegexKind
from regex_engine.src.regex_engine.domain.errors import NameNotDetectedError
from regex_engine.src.regex_engine.ports.regex_registry import RegexRegistryRepository
from regex_engine.src.regex_engine.ports.regex_service import RegexService
from regex_engine.src.regex_engine.domain.models import EnsureIngredientResult, EnsureWordResult

logger = logging.getLogger("regex_orchestrator")


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
        unit_size, unit, condition, name = ingredient.unit_size, ingredient.unit, ingredient.condition, ingredient.name

        tasks = []
        if not name:
            raise NameNotDetectedError(ingredient=ingredient.raw_input)

        if unit_size:
            tasks.append(self._ensure_word_included_in_registry(RegexKind.UNIT_SIZE, unit_size))

        if unit:
            tasks.append(self._ensure_word_included_in_registry(RegexKind.UNIT, unit))

        if condition:
            tasks.append(self._ensure_word_included_in_registry(RegexKind.INGREDIENT_CONDITION, condition))

        tasks.append(
            self._ensure_word_included_in_registry(RegexKind.INGREDIENT_NAME, name)
        )

        results = await asyncio.gather(*tasks)
        self._log_ensure_items(results, context=ingredient.raw_input)

        return self._build_ensure_output(results, ingredient.raw_input)


    async def _ensure_word_included_in_registry(self, kind: RegexKind, value: str) -> EnsureWordResult:
        return await self._services[kind].ensure_word_included_in_registry(value)

    def _build_ensure_output(self, ensure_results: list[EnsureWordResult], raw_input: str) -> EnsureIngredientResult:
        name = next(r for r in ensure_results if r.kind == RegexKind.INGREDIENT_NAME)
        return EnsureIngredientResult(raw_input=raw_input, name=name, items=ensure_results)

    def _log_ensure_items(self, items: list[EnsureWordResult], *, context: str) -> None:
        for item in items:
            status, stem = item.status, item.stem

            logger.info("[%s] %s=%s -> %s (stem: %s)",
                        context, item.kind, item.word, status.name, stem
                        )
