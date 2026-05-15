from dataclasses import dataclass
from uuid import UUID, uuid4

from regex_engine.domain.enums import Category


@dataclass
class CategorizedIngredient:
    id: UUID
    stem: str
    category:Category

    @classmethod
    def create(cls,
               *,
               stem: str,
               category: Category =  Category.UNKNOWN
               ) -> "CategorizedIngredient":
        return cls(
            id=uuid4(),
            stem=stem,
            category=category
        )

