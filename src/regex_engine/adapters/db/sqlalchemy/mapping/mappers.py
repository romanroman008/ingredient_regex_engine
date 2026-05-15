from regex_engine.adapters.db.sqlalchemy.mapping.mapping_types import (
    MappingResult,
    RecordMappingIssue,
)
from regex_engine.adapters.db.sqlalchemy.models import CategorizedIngredientRecord, RegexEntryRecord
from regex_engine.domain.enums import Category, RegexKind
from regex_engine.domain.models.categorized_ingredient import CategorizedIngredient
from regex_engine.domain.models.regex_entry import RegexEntry
from regex_engine.domain.models.regex_registry_default import RegexRegistryDefault
from regex_engine.ports.regex_registry import RegexRegistry, RegexRegistryReader


def regex_registry_to_records(registry:RegexRegistryReader):
    return [
        regex_entry_to_record(entry, registry.kind)
        for entry in registry.get_all()
    ]

def update_record_from_entry(record: RegexEntryRecord, entry:RegexEntry) -> None:
    record.stem = entry.stem
    record.variants = list(entry.variants)
    record.pattern = entry.pattern.pattern


def regex_entry_to_record(entry:RegexEntry, kind: RegexKind) -> RegexEntryRecord:
    return RegexEntryRecord(
        id=entry.id,
        regex_kind=kind.value,
        stem=entry.stem,
        variants=entry.variants,
        pattern=entry.pattern.pattern,
    )

def records_to_regex_registry(records: list[RegexEntryRecord], kind:RegexKind) -> RegexRegistry:
    return RegexRegistryDefault(
        kind=kind,
        entries=[
            record_to_regex_entry(record)
            for record in records
        ],
    )


def record_to_regex_entry(record:RegexEntryRecord) -> RegexEntry:
    return RegexEntry(
        stem=record.stem,
        variants=record.variants,
        entry_id=record.id
    )


def category_to_record(categorized_ingredient:CategorizedIngredient) -> CategorizedIngredientRecord:
    return CategorizedIngredientRecord(
        id=categorized_ingredient.id,
        stem=categorized_ingredient.stem,
        category=categorized_ingredient.category,
    )

def record_to_categorized_ingredient(record:CategorizedIngredientRecord) -> CategorizedIngredient:
    return CategorizedIngredient(
        id=record.id,
        stem=record.stem,
        category=Category(record.category),
    )

def records_to_categorized_ingredients(records:list[CategorizedIngredientRecord]) -> MappingResult:
    items = []
    issues = []
    for record in records:
        try:
            ingredient = record_to_categorized_ingredient(record)
            items.append(ingredient)

        except ValueError as e:
            issues.append(
                RecordMappingIssue(
                    record_id=record.id,
                    field=CategorizedIngredientRecord.category.key,
                    raw_value=record.category,
                    target_type=CategorizedIngredient,
                    reason=str(e),
                )
            )
            continue


    return MappingResult(items=items, issues=issues)
