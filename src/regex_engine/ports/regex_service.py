from typing import Protocol

from regex_engine.src.regex_engine.domain.enums import RegexKind
from regex_engine.src.regex_engine.domain.models.regex_registry import RegexRegistry
from regex_engine.src.regex_engine.domain.models import EnsureWordResult



class RegexService(Protocol):
    kind:RegexKind
    async def ensure_word_included_in_registry(self, word:str) -> EnsureWordResult:...
    @property
    def registry(self) -> RegexRegistry: ...
    @registry.setter
    def registry(self, registry:RegexRegistry) -> None: ...
