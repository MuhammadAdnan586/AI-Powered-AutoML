"""
Database Connection & Session Management
SQLAlchemy + MySQL
"""
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from app.config.settings import settings
import logging

logger = logging.getLogger(__name__)

# Create engine with connection pooling
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,          # Test connections before use
    pool_recycle=3600,           # Recycle connections every 1 hour
    echo=settings.APP_DEBUG,     # Log SQL in debug mode
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# Base class for all models
Base = declarative_base()


def get_db():
    """
    FastAPI dependency: provides a DB session per request.
    Automatically closes session after request.
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        db.close()


def create_tables():
    """Create all tables defined in models"""
    from app.auth.models import User, RefreshToken
    from app.datasets.models import Dataset, DatasetVersion
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Database tables created successfully")


def drop_tables():
    """Drop all tables (use with caution!)"""
    Base.metadata.drop_all(bind=engine)
    logger.warning("⚠️ All database tables dropped")
