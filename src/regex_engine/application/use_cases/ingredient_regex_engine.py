import logging
from dataclasses import fields

from regex_engine.adapters.input_adapters.types import EngineInput
from regex_engine.domain.enums import Category
from regex_engine.domain.errors import CategorizingError

from regex_engine.domain.models.registry_container import RegistryContainer
from regex_engine.domain.models.resolved_ingredient import ResolvedIngredient
from regex_engine.ports.categories_repository import CategoryRepository

from regex_engine.ports.categorizer import Categorizer
from regex_engine.ports.filter_engine import FilterEngine
from regex_engine.ports.input_adapter import InputAdapter
from regex_engine.ports.regex_registry import RegexRegistryRepository

logger = logging.getLogger(__name__)

def resolve_iterations(iterations:int, ingredients_number:int):
    if iterations < ingredients_number:
        return iterations
    return ingredients_number



class IngredientRegexEngine:
    def __init__(self,
        filter_engine:FilterEngine,
        categorizer:Categorizer,
        input_adapter:InputAdapter,
        regex_repository:RegexRegistryRepository,
        registries:RegistryContainer,
        category_repository:CategoryRepository,
        categorized_stems:dict[str, Category],
                 ):
        self._filter_engine = filter_engine
        self._categorizer:Categorizer = categorizer
        self._input_adapter = input_adapter
        self._regex_repository = regex_repository
        self._registries = registries
        self._category_repository = category_repository
        self._categorized_stems = categorized_stems



    async def process(self, data:EngineInput, iterations:int = 10) -> list[ResolvedIngredient]:
        ingredients = self._input_adapter.to_records(data)

        iterations = resolve_iterations(iterations, len(ingredients))

        resolved_ingredients = await self._filter_engine.filter_records(ingredients, iterations)

        return resolved_ingredients

    async def categorize(self) -> None:
        categorized = {}
        for ingredient in self._registries.ingredient_registry.get_all():
            category = self._categorized_stems.get(ingredient.stem)
            if category and category != Category.UNKNOWN:
                continue

            category = Category.UNKNOWN
            try:
                category = await self._categorizer.categorize(ingredient.stem)

            except CategorizingError as e:
                logger.error(
                    "Ingredient categorizing failed"
                        "Category set to UNKNOWN",
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
                continue

            finally:
                categorized[ingredient.stem] = category



    def save_registries(self) -> None:
        for field in fields(self._registries):
            name = field.name
            registry = getattr(self._registries, name)
            self._regex_repository.save(registry)

    def save_categories(self) -> None:
        self._category_repository.save(self._categorized_stems)



















