from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
from dotenv import load_dotenv
import os
import logging

logger = logging.getLogger(__name__)

# .env file load karo
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '..', '.env'))

DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:password@localhost:3306/automl_saas")
APP_DEBUG = os.getenv("APP_DEBUG", "false").lower() == "true"

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=APP_DEBUG,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
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
    from app.auth.models import User, RefreshToken
    from app.datasets.models import Dataset, DatasetVersion, ProcessedDataset, EngineeredDataset
    from app.datasets.models_module2 import TrainingSession, ModelResult
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Database tables created successfully")

def drop_tables():
    Base.metadata.drop_all(bind=engine)