from pydantic import BaseModel

from regex_engine.domain.enums import Category


class CategorizedIngredientAgent(BaseModel):
    category: Category
    name: str
    description: str
    reason: str
