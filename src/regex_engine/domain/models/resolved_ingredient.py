from dataclasses import field, dataclass
from typing import Optional

from regex_engine.domain.models.orchestrator import EnsureWordResult

@dataclass(frozen=True, slots=True)
class ResolvedIngredient:
    raw_input:str
    amount:float = -1
    unit_size:Optional[EnsureWordResult] = None
    unit:Optional[EnsureWordResult]= None
    condition:Optional[EnsureWordResult] = None
    name:Optional[EnsureWordResult] = None
    extra:str = ""
    issues:list[Exception] = field(default_factory=list)



