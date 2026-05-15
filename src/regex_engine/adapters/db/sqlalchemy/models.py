from __future__ import annotations

from uuid import UUID

from sqlalchemy import String
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql.schema import ForeignKey


class Base(DeclarativeBase):
    pass


class RegexEntryRecord(Base):
    __tablename__ = 'regex_entries'
    id: Mapped[UUID] = mapped_column(primary_key=True)
    regex_kind: Mapped[str] = mapped_column(primary_key=True)
    stem: Mapped[str] = mapped_column(unique=True,  nullable=False)
    variants: Mapped[list[str]] = mapped_column(
        ARRAY(String),
        nullable=False,
    )
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



class CategorizedIngredientRecord(Base):
    __tablename__ = 'categorized_ingredients'
    id: Mapped[UUID] = mapped_column(primary_key=True)
    stem:Mapped[str] = mapped_column( nullable=False, unique=True)
    category:Mapped[str] = mapped_column(nullable=False)

    regex_entries: Mapped[RegexEntryRecord] = relationship(
        back_populates="categorized_ingredient",
    )


    def __repr__(self):
        return f"<CategorizedIngredient: id={self.id}, stem={self.stem}, category={self.category}>"
