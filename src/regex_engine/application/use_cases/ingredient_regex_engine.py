import logging
from dataclasses import fields

from regex_engine.adapters.input_adapters.types import EngineInput
from regex_engine.domain.enums import Category
from regex_engine.domain.errors import CategorizingError
from regex_engine.domain.models.registry_container import RegistryContainerReader

from regex_engine.domain.models.resolved_ingredient import ResolvedIngredient
from regex_engine.ports.categories_repository import CategoryRepository

from regex_engine.ports.categorizer import Categorizer
from regex_engine.ports.categorizer_service import CategorizerService
from regex_engine.ports.filter_engine import FilterEngine
from regex_engine.ports.input_adapter import InputAdapter
from regex_engine.ports.regex_registry import RegexRegistryRepository

logger = logging.getLogger(__name__)


class IngredientRegexEngine:
    def __init__(self,
        filter_engine:FilterEngine,
        input_adapter:InputAdapter,
        regex_repository:RegexRegistryRepository,
        registries:RegistryContainerReader,
        categorizer_service:CategorizerService,
                 ):
        self._filter_engine = filter_engine
        self._input_adapter = input_adapter
        self._regex_repository = regex_repository
        self._registries = registries
        self._category_service = categorizer_service


    async def process(self, data:EngineInput, iterations:int = 10) -> list[ResolvedIngredient]:
        ingredients = self._input_adapter.to_records(data)

        iterations = min(iterations, len(ingredients))

        resolved_ingredients = await self._filter_engine.filter_records(ingredients, iterations)

        return resolved_ingredients

    async def categorize_registries(self) -> dict[str, Category]:
        return await self._category_service.categorize(self._registries.ingredient_registry)


    def save_registries(self) -> None:
        for field in fields(self._registries):
            name = field.name
            registry = getattr(self._registries, name)
            self._regex_repository.save(registry)


    def save_categories(self) -> None:
        self._category_service.save()



















