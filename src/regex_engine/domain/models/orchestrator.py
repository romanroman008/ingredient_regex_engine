from dataclasses import dataclass, field
from typing import Optional

from regex_engine.domain.enums import RegexKind, EnsureStatus


@dataclass(slots=True, frozen=True)
class EnsureWordResult:
    kind:RegexKind
    status:EnsureStatus
    stem:str
    word:str
    exception:Optional[Exception] = None



@dataclass(slots=True, frozen=True)
class EnsureIngredientResult:
    raw_input:str
    name:EnsureWordResult
    items:dict[RegexKind, EnsureWordResult]


