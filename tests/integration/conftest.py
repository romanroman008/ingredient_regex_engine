from __future__ import annotations

import os
from collections.abc import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from testcontainers.postgres import PostgresContainer

from regex_engine.adapters.db.sqlalchemy.models import Base


@pytest.fixture(scope="session")
def postgres_url() -> Generator[str, None, None]:
    configured_url = os.getenv("TEST_DATABASE_URL")
    if configured_url:
        yield configured_url
        return

    image = os.getenv("POSTGRES_IMAGE", "postgres:16-alpine")

    with PostgresContainer(image, driver="psycopg") as postgres:
        yield postgres.get_connection_url()


@pytest.fixture(scope="session")
def engine(postgres_url: str) -> Generator[Engine, None, None]:
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
def session_factory(engine: Engine) -> Generator[sessionmaker[Session], None, None]:
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
def db_session(session_factory: sessionmaker[Session]) -> Generator[Session, None, None]:
    with session_factory() as session:
        yield session