import logging
from sqlmodel import SQLModel, Session, create_engine
from app.config import get_settings
from contextlib import contextmanager

logger = logging.getLogger(__name__)

_settings = get_settings()
engine_kwargs = {
    "echo": _settings.env.lower() in ["dev", "development", "test", "testing", "staging"],
}
if not _settings.database_uri.startswith("sqlite"):
    engine_kwargs["pool_size"] = _settings.db_pool_size
    engine_kwargs["max_overflow"] = _settings.db_additional_overflow
    engine_kwargs["pool_timeout"] = _settings.db_pool_timeout
    engine_kwargs["pool_recycle"] = _settings.db_pool_recycle

engine = create_engine(_settings.database_uri, **engine_kwargs)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def drop_all():
    SQLModel.metadata.drop_all(bind=engine)
    
def _session_generator():
    with Session(engine) as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()

def get_session():
    yield from _session_generator()

@contextmanager
def get_cli_session():
    yield from _session_generator()
