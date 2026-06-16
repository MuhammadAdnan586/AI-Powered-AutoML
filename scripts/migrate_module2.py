"""
Module 2 - Database Migration
Run this script to add Module 2 tables to existing database

Usage:
    python scripts/migrate_module2.py
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from sqlalchemy import text
from app.database.connection import engine, SessionLocal
from app.database.base import Base

# Import all models so SQLAlchemy knows about them
from app.auth.models import User
from app.datasets.models import Dataset

# Module 2 models
from app.datasets.models_module2 import ProcessedDataset, EngineeredDataset, TrainingSession, ModelResult


def run_migration():
    print("=" * 60)
    print("Module 2 - Database Migration")
    print("=" * 60)

    try:
        # Create all tables (skips existing ones)
        Base.metadata.create_all(bind=engine)
        print("✅ All Module 2 tables created successfully")

        # Verify tables exist
        db = SessionLocal()
        tables_to_check = [
            "processed_datasets",
            "engineered_datasets",
            "training_sessions",
            "model_results"
        ]

        for table in tables_to_check:
            try:
                result = db.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                print(f"   ✓ Table '{table}' exists — {count} rows")
            except Exception as e:
                print(f"   ✗ Table '{table}' — ERROR: {e}")

        db.close()

        print("\n✅ Migration complete!")
        print("\nNew tables added:")
        print("  → processed_datasets   (preprocessing results)")
        print("  → engineered_datasets  (feature engineering results)")
        print("  → training_sessions    (automl training sessions)")
        print("  → model_results        (individual model metrics)")

    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        raise


def add_dataset_relationships():
    """Add back_populates to Dataset model if needed."""
    print("\nNote: Ensure Dataset model in Module 1 has:")
    print("  processed_datasets = relationship('ProcessedDataset', back_populates='original_dataset')")


if __name__ == "__main__":
    run_migration()
    add_dataset_relationships()
