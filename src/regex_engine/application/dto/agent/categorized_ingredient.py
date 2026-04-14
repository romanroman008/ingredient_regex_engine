from regex_engine.domain.enums import Category
from pydantic import BaseModel

class CategorizedIngredient(BaseModel):
    category: Category
    name: str
    description: str
    reason: str