import re
import socket
from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.db.base import Base

engine = None
SessionLocal = None
ACTIVE_DB_TYPE = "unknown"


def _is_service_reachable(url: str, timeout: float = 0.5) -> bool:
    """Quick socket probe to verify if MySQL host/port is accepting connections."""
    match = re.search(r"@([^:/]+)(?::(\d+))?", url)
    if not match:
        return False
    host = match.group(1)
    port = int(match.group(2)) if match.group(2) else 3306
    if host == "localhost":
        host = "127.0.0.1"
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def init_db_engine():
    """Initializes SQLAlchemy engine with MySQL or automatic SQLite fallback."""
    global engine, SessionLocal, ACTIVE_DB_TYPE

    if SessionLocal is not None:
        return engine

    mysql_url = settings.DATABASE_URL
    mysql_connected = False

    if "mysql" in mysql_url.lower():
        if _is_service_reachable(mysql_url, timeout=0.8):
            try:
                test_engine = create_engine(
                    mysql_url,
                    pool_size=10,
                    max_overflow=20,
                    pool_recycle=3600,
                    pool_pre_ping=True
                )
                with test_engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                engine = test_engine
                ACTIVE_DB_TYPE = "mysql"
                mysql_connected = True
                logger.info("Successfully connected to MySQL database with connection pooling.")
            except Exception as exc:
                logger.warning(f"MySQL reachable on port but query test failed: {exc}")

    if not mysql_connected:
        if settings.DB_AUTO_FALLBACK_SQLITE:
            logger.info(f"MySQL not detected locally. Initializing SQLite storage: {settings.SQLITE_FALLBACK_URL}")
            sqlite_url = settings.SQLITE_FALLBACK_URL
            engine = create_engine(
                sqlite_url,
                connect_args={"check_same_thread": False}
            )
            ACTIVE_DB_TYPE = "sqlite"
        else:
            raise ConnectionError("MySQL connection failed and SQLite fallback is disabled.")

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Import all models to register with Base.metadata
    import backend.app.models  # noqa: F401
    Base.metadata.create_all(bind=engine)
    logger.info(f"Database schema initialized successfully using {ACTIVE_DB_TYPE}.")
    return engine


# Auto-initialize on import so SessionLocal is immediately callable
init_db_engine()


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency for yielding database session with automatic transaction management."""
    if SessionLocal is None:
        init_db_engine()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_session() -> Session:
    """Helper to get a standalone session."""
    if SessionLocal is None:
        init_db_engine()
    return SessionLocal()
