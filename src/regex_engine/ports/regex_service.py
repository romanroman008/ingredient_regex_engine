from typing import Protocol

from regex_engine.domain.enums import RegexKind
from regex_engine.domain.models.orchestrator import EnsureWordResult
from regex_engine.domain.models.regex_registry import RegexRegistry




class RegexService(Protocol):
    @property
    def kind(self) -> RegexKind: ...
    async def ensure_word_included_in_registry(self, word:str) -> EnsureWordResult: ...





