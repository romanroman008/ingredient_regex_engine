from sqlalchemy.engine.base import Engine
from sqlalchemy.engine.create import create_engine
from sqlalchemy.orm.session import sessionmaker, Session


def create_db_engine(database_url:str) -> Engine:
    return create_engine(
        database_url,
        echo=True
    )


def create_session_factory(engine:Engine) -> sessionmaker[Session]:
    return sessionmaker(
        bind=engine,
        autflush=False,
        expire_on_commit=False,
    )