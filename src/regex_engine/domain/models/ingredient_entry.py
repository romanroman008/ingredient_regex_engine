from dataclasses import dataclass
from typing import Iterable

from regex_engine.domain.enums import Category
from regex_engine.domain.models.regex_entry import RegexEntry


@dataclass(eq=False)
class IngredientEntry(RegexEntry):
    def __init__(self, stem:str,
                 variants:Iterable[str],
                 category:Category):

        super().__init__(stem, variants)
        self.category = category

    category:Category = Category.OTHER