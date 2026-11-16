"""
Database connection and session management for NOC system using SQLite & SQLAlchemy.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from backend.config import settings
from backend.utils.logger import logger

# SQLite connect args to allow multithreaded access
connect_args = {"check_same_thread": False}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=False,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Dependency for API endpoints to get DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Create all tables in the SQLite database."""
    from backend import models  # noqa: F401
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized successfully at: %s", settings.DATABASE_PATH)
