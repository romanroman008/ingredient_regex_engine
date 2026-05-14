from uuid import UUID

from sqlalchemy.orm import declarative_base, mapped_column, Mapped, relationship
from sqlalchemy.sql.schema import ForeignKey

from regex_engine.adapters.db.sqlalchemy.models.category_record import CategorizedIngredientRecord

Base = declarative_base()

class RegexEntryRecord(Base):
    __tablename__ = 'regex_entries'
    id: Mapped[UUID] = mapped_column(primary_key=True)
    regex_kind: Mapped[str] = mapped_column(primary_key=True)
    stem: Mapped[str] = mapped_column(unique=True, notnull=True)
    variants: Mapped[list[str]]
    pattern:Mapped[str]

    categorized_ingredient_id: Mapped[UUID] = mapped_column(
        ForeignKey("categorized_ingredients.id"),
        nullable=True,
    )

    categorized_ingredient: Mapped[CategorizedIngredientRecord | None] = relationship(
        back_populates="regex_entries",
    )


    def __repr__(self) -> str:
        return f"<RegexEntry id={self.id} name={self.name} variants={self.variants}>"




