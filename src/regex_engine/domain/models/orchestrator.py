from dataclasses import dataclass

from regex_engine.src.regex_engine.domain.enums import RegexKind, EnsureStatus


@dataclass(slots=True, frozen=True)
class EnsureWordResult:
    kind:RegexKind
    status:EnsureStatus
    stem:str
    word:str


@dataclass(slots=True, frozen=True)
class EnsureIngredientResult:
    raw_input:str
    name:EnsureWordResult
    items:list[EnsureWordResult]