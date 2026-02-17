from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class IngredientRecord:
    name:str
    count:int
    remainder:Optional[str] = None
    iterated:bool = False
    attempts: int = 0
