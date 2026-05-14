from uuid import UUID

from sqlalchemy.orm import declarative_base, mapped_column, Mapped, relationship

from regex_engine.adapters.db.sqlalchemy.models.regex_entry_record import RegexEntryRecord

Base = declarative_base()

class CategorizedIngredientRecord(Base):
    __tablename__ = 'categorized_ingredients'
    id: Mapped[UUID] = mapped_column(primary_key=True)
    stem:Mapped[str] = mapped_column(not_null=True, unique=True)
    category:Mapped[str] = mapped_column(not_null=True)

    regex_entries: Mapped[RegexEntryRecord] = relationship(
        back_populates="categorized_ingredients",
    )


    def __repr__(self):
        return f"<CategorizedIngredient: id={self.id}, stem={self.stem}, category={self.category}>"
