

import os
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from testcontainers.postgres import PostgresContainer

from regex_engine.adapters.db.sqlalchemy.models import (
    Base,
    CategorizedIngredientRecord,
    RegexEntryRecord,
)
from regex_engine.adapters.db.sqlalchemy.sql_category_repository import SQLAlchemyCategoryRepository
from regex_engine.domain.enums import Category, RegexKind
from regex_engine.domain.models.categorized_ingredient import CategorizedIngredient


@pytest.fixture(scope="session")
def postgres_url():
    configured_url = os.getenv("TEST_DATABASE_URL")
    if configured_url:
        yield configured_url
        return

    image = os.getenv("POSTGRES_IMAGE", "postgres:16-alpine")

    with PostgresContainer(image, driver="psycopg") as postgres:
        yield postgres.get_connection_url()


@pytest.fixture(scope="session")
def engine(postgres_url: str):
    engine = create_engine(
        postgres_url,
        future=True,
        pool_pre_ping=True,
    )

    Base.metadata.create_all(engine)

    yield engine

    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def session_factory(engine):
    connection = engine.connect()
    transaction = connection.begin()

    factory = sessionmaker(
        bind=connection,
        expire_on_commit=False,
        join_transaction_mode="create_savepoint",
    )

    try:
        yield factory
    finally:
        transaction.rollback()
        connection.close()


@pytest.fixture
def db_session(session_factory) -> Session:
    with session_factory() as session:
        yield session


@pytest.fixture
def repository(session_factory) -> SQLAlchemyCategoryRepository:
    return SQLAlchemyCategoryRepository(session_factory)


def make_ingredient(
    *,
    stem: str,
    category: Category = Category.DAIRY,
) -> CategorizedIngredient:
    return CategorizedIngredient(
        id=uuid4(),
        stem=stem,
        category=category,
    )


def make_regex_entry(
    *,
    stem: str,
    regex_kind: RegexKind = RegexKind.INGREDIENT_NAME,
) -> RegexEntryRecord:
    return RegexEntryRecord(
        id=uuid4(),
        regex_kind=regex_kind.value,
        stem=stem,
        variants=[stem],
        pattern=stem,
    )


def get_category_record(
    session: Session,
    ingredient_id,
) -> CategorizedIngredientRecord | None:
    return session.scalar(
        select(CategorizedIngredientRecord).where(
            CategorizedIngredientRecord.id == ingredient_id
        )
    )


def get_regex_entry(
    session: Session,
    *,
    stem: str,
    regex_kind: RegexKind,
) -> RegexEntryRecord | None:
    return session.scalar(
        select(RegexEntryRecord).where(
            RegexEntryRecord.stem == stem,
            RegexEntryRecord.regex_kind == regex_kind.value,
        )
    )


def test_load_returns_categorized_ingredients_indexed_by_stem(
    db_session: Session,
    repository: SQLAlchemyCategoryRepository,
):
    ingredient_id = uuid4()

    db_session.add(
        CategorizedIngredientRecord(
            id=ingredient_id,
            stem="mleko",
            category=Category.DAIRY.value,
        )
    )
    db_session.commit()

    result = repository.load()

    assert result == {
        "mleko": CategorizedIngredient(
            id=ingredient_id,
            stem="mleko",
            category=Category.DAIRY,
        )
    }


def test_load_skips_invalid_category_records_and_logs_warning(
    db_session: Session,
    repository: SQLAlchemyCategoryRepository,
    caplog: pytest.LogCaptureFixture,
):
    db_session.add(
        CategorizedIngredientRecord(
            id=uuid4(),
            stem="dziwny-produkt",
            category="invalid-category",
        )
    )
    db_session.commit()

    result = repository.load()

    assert result == {}
    assert "Skipped 1 invalid records" in caplog.text
    assert "invalid-category" in caplog.text


def test_save_inserts_new_categorized_ingredient(
    db_session: Session,
    repository: SQLAlchemyCategoryRepository,
):
    ingredient = make_ingredient(
        stem="mleko",
        category=Category.DAIRY,
    )

    repository.save({"mleko": ingredient})

    db_session.expire_all()
    saved = get_category_record(db_session, ingredient.id)

    assert saved is not None
    assert saved.id == ingredient.id
    assert saved.stem == "mleko"
    assert saved.category == Category.DAIRY.value


def test_save_updates_existing_categorized_ingredient(
    db_session: Session,
    repository: SQLAlchemyCategoryRepository,
):
    ingredient_id = uuid4()

    db_session.add(
        CategorizedIngredientRecord(
            id=ingredient_id,
            stem="mleko",
            category=Category.DAIRY.value,
        )
    )
    db_session.commit()

    repository.save(
        {
            "jogurt": CategorizedIngredient(
                id=ingredient_id,
                stem="jogurt",
                category=Category.PROCESSED,
            )
        }
    )

    db_session.expire_all()
    saved = get_category_record(db_session, ingredient_id)

    assert saved is not None
    assert saved.stem == "jogurt"
    assert saved.category == Category.PROCESSED.value


def test_save_deletes_removed_categorized_ingredient(
    db_session: Session,
    repository: SQLAlchemyCategoryRepository,
):
    ingredient_id = uuid4()

    db_session.add(
        CategorizedIngredientRecord(
            id=ingredient_id,
            stem="mleko",
            category=Category.DAIRY.value,
        )
    )
    db_session.commit()

    repository.save({})

    db_session.expire_all()
    saved = get_category_record(db_session, ingredient_id)

    assert saved is None


def test_save_rejects_duplicated_categorized_ingredient_ids(
    repository: SQLAlchemyCategoryRepository,
):
    duplicated_id = uuid4()

    first = CategorizedIngredient(
        id=duplicated_id,
        stem="mleko",
        category=Category.DAIRY,
    )
    second = CategorizedIngredient(
        id=duplicated_id,
        stem="jogurt",
        category=Category.PROCESSED,
    )

    with pytest.raises(
        ValueError,
        match="CategorizedIngredients contains duplicated ids",
    ):
        repository.save(
            {
                "mleko": first,
                "jogurt": second,
            }
        )


def test_save_is_idempotent_for_same_input(
    db_session: Session,
    repository: SQLAlchemyCategoryRepository,
):
    ingredient = make_ingredient(
        stem="mleko",
        category=Category.DAIRY,
    )

    repository.save({"mleko": ingredient})
    repository.save({"mleko": ingredient})

    db_session.expire_all()
    records = list(db_session.scalars(select(CategorizedIngredientRecord)))

    assert len(records) == 1
    assert records[0].id == ingredient.id
    assert records[0].stem == "mleko"
    assert records[0].category == Category.DAIRY.value


def test_save_attaches_new_category_to_matching_ingredient_name_regex_entry(
    db_session: Session,
    repository: SQLAlchemyCategoryRepository,
):
    regex_entry = make_regex_entry(
        stem="mleko",
        regex_kind=RegexKind.INGREDIENT_NAME,
    )
    ingredient = make_ingredient(
        stem="mleko",
        category=Category.DAIRY,
    )

    db_session.add(regex_entry)
    db_session.commit()

    repository.save({"mleko": ingredient})

    db_session.expire_all()
    saved_entry = get_regex_entry(
        db_session,
        stem="mleko",
        regex_kind=RegexKind.INGREDIENT_NAME,
    )

    assert saved_entry is not None
    assert saved_entry.categorized_ingredient_id == ingredient.id


def test_save_does_not_attach_category_to_non_ingredient_name_regex_entry(
    db_session: Session,
    repository: SQLAlchemyCategoryRepository,
):
    regex_entry = make_regex_entry(
        stem="mleko",
        regex_kind=RegexKind.UNIT,
    )
    ingredient = make_ingredient(
        stem="mleko",
        category=Category.DAIRY,
    )

    db_session.add(regex_entry)
    db_session.commit()

    repository.save({"mleko": ingredient})

    db_session.expire_all()
    saved_entry = get_regex_entry(
        db_session,
        stem="mleko",
        regex_kind=RegexKind.UNIT,
    )

    assert saved_entry is not None
    assert saved_entry.categorized_ingredient_id is None


def test_save_does_not_attach_regex_entry_with_different_stem(
    db_session: Session,
    repository: SQLAlchemyCategoryRepository,
):
    regex_entry = make_regex_entry(
        stem="maslo",
        regex_kind=RegexKind.INGREDIENT_NAME,
    )
    ingredient = make_ingredient(
        stem="mleko",
        category=Category.DAIRY,
    )

    db_session.add(regex_entry)
    db_session.commit()

    repository.save({"mleko": ingredient})

    db_session.expire_all()
    saved_entry = get_regex_entry(
        db_session,
        stem="maslo",
        regex_kind=RegexKind.INGREDIENT_NAME,
    )

    assert saved_entry is not None
    assert saved_entry.categorized_ingredient_id is None