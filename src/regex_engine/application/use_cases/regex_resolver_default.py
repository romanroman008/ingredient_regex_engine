from regex_engine.domain.const import TRASH_RE, ENUM_TOKEN_RE, AND_CONJ_RE, OR_CONJ_RE, \
    AND_CONJ_BETWEEN_NUMBERS_RE
from regex_engine.domain.enums import RegexKind
from regex_engine.ports.regex_registry import RegexRegistryReader


def is_number(s:str) -> bool:
    try:
        float(s)
        return True
    except ValueError:
        return False

class RegexResolverDefault:
    def __init__(
            self,
            ingredient_names: RegexRegistryReader,
            ingredient_conditions: RegexRegistryReader,
            unit_sizes: RegexRegistryReader,
            units: RegexRegistryReader,
            or_conjunctions: RegexRegistryReader,
            and_conjunctions: RegexRegistryReader
    ):
        self.pipeline: list[tuple[RegexKind, RegexRegistryReader]] = [
            (RegexKind.INGREDIENT_NAME, ingredient_names),
            (RegexKind.INGREDIENT_CONDITION, ingredient_conditions),
            (RegexKind.UNIT_SIZE, unit_sizes),
            (RegexKind.UNIT, units),
            (RegexKind.OR_CONJUNCTIONS, or_conjunctions),
            (RegexKind.AND_CONJUNCTIONS, and_conjunctions),
        ]

    def standardize(self, ingredient: str) -> str:
        result = ingredient
        for kind, lookup in self.pipeline:
            result = lookup.swap_match(result, kind.name)
        return result

    def can_be_standardized(self, ingredient: str) -> bool:
        standardized = self.standardize(ingredient)
        remainders = ENUM_TOKEN_RE.sub("", standardized).strip()
        clean = TRASH_RE.sub("", remainders).strip()

        if not clean or is_number(clean):
            return True
        return False

    def get_remainder(self, ingredient: str) -> str:
        standardized = self.standardize(ingredient)
        remainders = ENUM_TOKEN_RE.sub("", standardized).strip()
        clean = TRASH_RE.sub("", remainders).strip()
        return clean

    def contains_conjunction(self, ingredient: str) -> bool:
        if AND_CONJ_RE.search(ingredient) or OR_CONJ_RE.search(ingredient):
            return True
        return False

    def and_conjunction_between_numbers(self, ingredient: str) -> bool:
        if AND_CONJ_BETWEEN_NUMBERS_RE.search(ingredient):
            return True
        return False