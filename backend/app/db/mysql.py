from collections.abc import Generator
import logging

from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings

logger = logging.getLogger(__name__)
database_mode = "mysql"


class Base(DeclarativeBase):
    pass


def _build_engine():
    global database_mode

    candidates = []
    if settings.database_url:
        candidates.append(("configured", settings.database_url))
    else:
        candidates.append(("mysql", settings.sqlalchemy_database_uri))

    last_error = None
    for label, uri in candidates:
        connect_args = {"check_same_thread": False, "timeout": 30} if uri.startswith("sqlite") else {}
        if uri.startswith("sqlite:///"):
            sqlite_path = uri.removeprefix("sqlite:///")
            from pathlib import Path

            Path(sqlite_path).parent.mkdir(parents=True, exist_ok=True)
        engine = create_engine(uri, pool_pre_ping=True, connect_args=connect_args)
        try:
            with engine.connect():
                database_mode = label
                logger.warning("Database engine ready: %s", label)
                return engine
        except SQLAlchemyError as exc:
            last_error = exc
            logger.warning("Database engine %s unavailable, trying next option: %s", label, exc)

    logger.warning("Falling back to JSON-backed local state because relational database is unavailable.")
    database_mode = "json-fallback"
    return create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


engine = _build_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    import app.models  # noqa: F401

    Base.metadata.create_all(bind=engine)


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
