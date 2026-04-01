from regex_engine.application.use_cases.regex_service_default import RegexServiceDefault
from regex_engine.domain.enums import RegexKind
from regex_engine.domain.models.ingredient_regex_registry import IngredientRegexRegistry
from regex_engine.ports.token_normalizer import TokenNormalizer


class IngredientRegexService(RegexServiceDefault):
    def __init__(self, normalizer: TokenNormalizer):
        super().__init__(RegexKind.INGREDIENT_NAME, normalizer)
        self._registry: IngredientRegexRegistry | None = None

    @property
    def registry(self) -> IngredientRegexRegistry:
        if not self._registry:
            raise RuntimeError("Registry is not set for kind: %s" % self.kind)
        return self._registry

    @registry.setter
    def registry(self, registry: IngredientRegexRegistry) -> None:
        self._registry = registry