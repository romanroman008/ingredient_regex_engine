from dataclasses import dataclass

from regex_engine.src.regex_engine.domain.enums import Category
from regex_engine.src.regex_engine.domain.models.regex_entry import RegexEntry

@dataclass(eq=False)
class IngredientEntry(RegexEntry):
    category:Category = Category.OTHER