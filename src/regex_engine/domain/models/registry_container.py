from dataclasses import dataclass


from regex_engine.domain.models.regex_registry import RegexRegistry
from regex_engine.ports.regex_registry import RegexRegistryReader


@dataclass(slots=True)
class RegistryContainer:
    ingredient_registry: RegexRegistryReader
    unit_registry: RegexRegistryReader
    unit_size_registry: RegexRegistryReader
    condition_registry: RegexRegistryReader
    or_conjunctions_registry: RegexRegistryReader
    and_conjunctions_registry: RegexRegistryReader