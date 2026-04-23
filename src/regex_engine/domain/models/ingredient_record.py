from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class IngredientRecord:
    name:str
    count:int
