from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from regex_engine.adapters.db.sqlalchemy.models import RegexEntryRecord
from regex_engine.adapters.db.sqlalchemy.sql_regex_repository import (
    SQLAlchemyRegexRepository,
)
from regex_engine.domain.enums import RegexKind
from regex_engine.domain.models.regex_entry import RegexEntry
from regex_engine.domain.models.regex_registry_default import RegexRegistryDefault


@pytest.fixture
def repository(session_factory) -> SQLAlchemyRegexRepository:
    return SQLAlchemyRegexRepository(session_factory)


def make_entry(
    *,
    stem: str,
    variants: list[str] | None = None,
    entry_id=None,
) -> RegexEntry:
    return RegexEntry(
        stem=stem,
        variants=variants or [stem],
        entry_id=entry_id or uuid4(),
    )


def make_registry(
    *,
    kind: RegexKind,
    entries: list[RegexEntry],
) -> RegexRegistryDefault:
    return RegexRegistryDefault(
        kind=kind,
        entries=entries,
    )


def make_record(
    *,
    stem: str,
    regex_kind: RegexKind,
    variants: list[str] | None = None,
    record_id=None,
    pattern: str | None = None,
) -> RegexEntryRecord:
    return RegexEntryRecord(
        id=record_id or uuid4(),
        regex_kind=regex_kind.value,
        stem=stem,
        variants=variants or [stem],
        pattern=pattern or stem,
    )


def get_record(
    session: Session,
    *,
    record_id,
    regex_kind: RegexKind,
) -> RegexEntryRecord | None:
    return session.scalar(
        select(RegexEntryRecord).where(
            RegexEntryRecord.id == record_id,
            RegexEntryRecord.regex_kind == regex_kind.value,
        )
    )


def get_all_records(session: Session) -> list[RegexEntryRecord]:
    return list(session.scalars(select(RegexEntryRecord)))


def test_load_returns_registry_for_requested_regex_kind_only(
    db_session: Session,
    repository: SQLAlchemyRegexRepository,
):
    ingredient_record = make_record(
        stem="mleko",
        regex_kind=RegexKind.INGREDIENT_NAME,
        variants=["mleko", "mleka"],
        pattern="mleko|mleka",
    )
    unit_record = make_record(
        stem="kg",
        regex_kind=RegexKind.UNIT,
        variants=["kg", "kilogram"],
        pattern="kg|kilogram",
    )

    db_session.add_all([ingredient_record, unit_record])
    db_session.commit()

    result = repository.load(RegexKind.INGREDIENT_NAME)

    entries = list(result.get_all())

    assert result.kind == RegexKind.INGREDIENT_NAME
    assert len(entries) == 1
    assert entries[0].id == ingredient_record.id
    assert entries[0].stem == "mleko"
    assert set(entries[0].variants) == {"mleko", "mleka"}


def test_save_inserts_new_regex_entries(
    db_session: Session,
    repository: SQLAlchemyRegexRepository,
):
    entry = make_entry(
        stem="mleko",
        variants=["mleko", "mleka"],
    )
    registry = make_registry(
        kind=RegexKind.INGREDIENT_NAME,
        entries=[entry],
    )

    repository.save(registry)

    db_session.expire_all()
    saved = get_record(
        db_session,
        record_id=entry.id,
        regex_kind=RegexKind.INGREDIENT_NAME,
    )

    assert saved is not None
    assert saved.id == entry.id
    assert saved.regex_kind == RegexKind.INGREDIENT_NAME.value
    assert saved.stem == "mleko"
    assert set(saved.variants) == {"mleko", "mleka"}
    assert saved.pattern == entry.pattern.pattern


def test_save_updates_existing_regex_entries_for_same_kind(
    db_session: Session,
    repository: SQLAlchemyRegexRepository,
):
    entry_id = uuid4()

    db_session.add(
        make_record(
            record_id=entry_id,
            regex_kind=RegexKind.INGREDIENT_NAME,
            stem="mleko",
            variants=["mleko"],
            pattern="mleko",
        )
    )
    db_session.commit()

    updated_entry = make_entry(
        entry_id=entry_id,
        stem="jogurt",
        variants=["jogurt", "jogurtu"],
    )
    registry = make_registry(
        kind=RegexKind.INGREDIENT_NAME,
        entries=[updated_entry],
    )

    repository.save(registry)

    db_session.expire_all()
    saved = get_record(
        db_session,
        record_id=entry_id,
        regex_kind=RegexKind.INGREDIENT_NAME,
    )

    assert saved is not None
    assert saved.stem == "jogurt"
    assert set(saved.variants) == {"jogurt", "jogurtu"}
    assert saved.pattern == updated_entry.pattern.pattern


def test_save_deletes_removed_regex_entries_for_same_kind(
    db_session: Session,
    repository: SQLAlchemyRegexRepository,
):
    removed_id = uuid4()

    db_session.add(
        make_record(
            record_id=removed_id,
            regex_kind=RegexKind.INGREDIENT_NAME,
            stem="mleko",
        )
    )
    db_session.commit()

    registry = make_registry(
        kind=RegexKind.INGREDIENT_NAME,
        entries=[],
    )

    repository.save(registry)

    db_session.expire_all()
    saved = get_record(
        db_session,
        record_id=removed_id,
        regex_kind=RegexKind.INGREDIENT_NAME,
    )

    assert saved is None


def test_save_does_not_modify_entries_from_other_regex_kinds(
    db_session: Session,
    repository: SQLAlchemyRegexRepository,
):
    shared_id = uuid4()

    ingredient_record = make_record(
        record_id=shared_id,
        regex_kind=RegexKind.INGREDIENT_NAME,
        stem="mleko",
        variants=["mleko"],
        pattern="mleko",
    )
    unit_record = make_record(
        record_id=shared_id,
        regex_kind=RegexKind.UNIT,
        stem="kg",
        variants=["kg"],
        pattern="kg",
    )

    db_session.add_all([ingredient_record, unit_record])
    db_session.commit()

    updated_ingredient_entry = make_entry(
        entry_id=shared_id,
        stem="jogurt",
        variants=["jogurt"],
    )
    registry = make_registry(
        kind=RegexKind.INGREDIENT_NAME,
        entries=[updated_ingredient_entry],
    )

    repository.save(registry)

    db_session.expire_all()

    saved_ingredient = get_record(
        db_session,
        record_id=shared_id,
        regex_kind=RegexKind.INGREDIENT_NAME,
    )
    saved_unit = get_record(
        db_session,
        record_id=shared_id,
        regex_kind=RegexKind.UNIT,
    )

    assert saved_ingredient is not None
    assert saved_ingredient.stem == "jogurt"

    assert saved_unit is not None
    assert saved_unit.stem == "kg"
    assert saved_unit.variants == ["kg"]
    assert saved_unit.pattern == "kg"


def test_save_rejects_duplicated_entry_ids(
    repository: SQLAlchemyRegexRepository,
):
    duplicated_id = uuid4()

    first = make_entry(
        entry_id=duplicated_id,
        stem="mleko",
    )
    second = make_entry(
        entry_id=duplicated_id,
        stem="jogurt",
    )

    registry = make_registry(
        kind=RegexKind.INGREDIENT_NAME,
        entries=[first, second],
    )

    with pytest.raises(
        ValueError,
        match="Regex registry contains duplicated entry ids",
    ):
        repository.save(registry)


def test_save_is_idempotent_for_same_registry(
    db_session: Session,
    repository: SQLAlchemyRegexRepository,
):
    entry = make_entry(
        stem="mleko",
        variants=["mleko", "mleka"],
    )
    registry = make_registry(
        kind=RegexKind.INGREDIENT_NAME,
        entries=[entry],
    )

    repository.save(registry)
    repository.save(registry)

    db_session.expire_all()
    records = get_all_records(db_session)

    assert len(records) == 1
    assert records[0].id == entry.id
    assert records[0].regex_kind == RegexKind.INGREDIENT_NAME.value
    assert records[0].stem == "mleko"
    assert set(records[0].variants) == {"mleko", "mleka"}
    assert records[0].pattern == entry.pattern.pattern