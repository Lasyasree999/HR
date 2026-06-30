"""
HireGenius AI — Database Connection
====================================
SQLAlchemy engine, session factory, and dependency injection for FastAPI.
Uses synchronous SQLAlchemy with pymysql driver.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from typing import Generator

from config import get_settings

settings = get_settings()

# Configure engine arguments based on DB type
engine_args = {
    "echo": settings.DEBUG,
}

if settings.DATABASE_URL.startswith("mysql"):
    engine_args.update({
        "pool_size": 10,
        "max_overflow": 20,
        "pool_pre_ping": True,
        "pool_recycle": 3600,
    })
elif settings.DATABASE_URL.startswith("sqlite"):
    engine_args.update({
        "connect_args": {"check_same_thread": False}
    })

# SQLAlchemy engine
engine = create_engine(
    settings.DATABASE_URL,
    **engine_args
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Declarative base for ORM models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a database session.
    Automatically closes the session after the request completes.

    Usage:
        @app.get("/endpoint")
        def endpoint(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database tables.
    Creates all tables defined by ORM models if they don't exist.
    Called during application startup.
    """
    from . import models  # noqa: F401 — Import models to register them
    Base.metadata.create_all(bind=engine)
