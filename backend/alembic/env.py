from logging.config import fileConfig
from sqlalchemy import create_engine, pool
from alembic import context
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database.connection import Base
from app.auth.models import User, RefreshToken
from app.datasets.models import Dataset, DatasetVersion

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline():
    context.configure(
        url="mysql+pymysql://root:F2a7t7i0%40@localhost:3306/automl_saas",
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    # Direct engine — no config interpolation issue
    connectable = create_engine(
        "mysql+pymysql://root:F2a7t7i0%40@localhost:3306/automl_saas",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()