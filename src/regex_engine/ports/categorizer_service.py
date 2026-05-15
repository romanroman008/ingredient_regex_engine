from typing import Protocol

from regex_engine.domain.models.categorized_ingredient import CategorizedIngredient
from regex_engine.ports.regex_registry import RegexRegistryReader


class CategorizerService(Protocol):
    async def categorize(self, ingredient_registry: RegexRegistryReader
    ) -> dict[str,CategorizedIngredient]: ...

    def save(self) -> None: ...
