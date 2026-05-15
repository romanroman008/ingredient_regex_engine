from sqlalchemy.orm.session import Session, sessionmaker
from sqlalchemy.sql.expression import select

from regex_engine.adapters.db.sqlalchemy.mapping.mappers import (
    records_to_regex_registry,
    regex_entry_to_record,
    update_record_from_entry,
)
from regex_engine.adapters.db.sqlalchemy.models import RegexEntryRecord
from regex_engine.domain.enums import RegexKind
from regex_engine.ports.regex_registry import RegexRegistry


class SQLAlchemyRegexRepository:
    def __init__(self, session_factory:sessionmaker[Session]):
        self._session_factory = session_factory


    def load(self, kind:RegexKind) -> RegexRegistry:
        with self._session_factory() as session:
            records = list(
                session.scalars(
                    select(RegexEntryRecord)
                    .where(RegexEntryRecord.regex_kind == kind.value)
                )
            )
            return records_to_regex_registry(records, kind)




    def save(self, registry: RegexRegistry) -> None:
        entries = list(registry.get_all())

        entries_by_id = {
            entry.id: entry
            for entry in entries
        }

        if len(entries_by_id) != len(entries):
            raise ValueError("Regex registry contains duplicated entry ids")

        with self._session_factory.begin() as session:
            existing_records = list(
                session.scalars(
                    select(RegexEntryRecord)
                    .where(
                        RegexEntryRecord.regex_kind == registry.kind.value
                    )
                )
            )

            existing_by_id = {
                record.id: record
                for record in existing_records
            }

            current_ids = set(entries_by_id)
            existing_ids = set(existing_by_id)

            for entry_id in current_ids - existing_ids:
                session.add(
                    regex_entry_to_record(
                        entry=entries_by_id[entry_id],
                        kind=registry.kind,
                    )
                )

            for entry_id in existing_ids & current_ids:
                update_record_from_entry(
                    record=existing_by_id[entry_id],
                    entry=entries_by_id[entry_id],
                )

            for entry_id in existing_ids - current_ids:
                session.delete(existing_by_id[entry_id])
