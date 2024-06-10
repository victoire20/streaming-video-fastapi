from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
import os
from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import quote_plus

config = context.config
env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)
    
from core import config as config_env
from core.database import Base
from core.models import User
from core.models import Genre
from core.models import Movie
from core.models import GenreMovie
from core.models import DownloadLink
from core.models import Comment
from core.models import Favorite

target_metadata = Base.metadata

def get_url():    
    db_user: str = os.getenv('DATABASE_USER')
    db_password: str = os.getenv('DATABASE_PASSWORD')
    db_name: str = os.getenv('DATABASE_DB')
    db_name_test: str = os.getenv('DATABASE_DB_TEST')
    db_host: str = os.getenv('DATABASE_SERVER')
    db_port: str = os.getenv('DATABASE_PORT')
    # return f"postgresql://{db_user}:{quote_plus(db_password)}@{db_host}:{db_port}/{db_name_test}"
    return 'sqlite:///./zoneanimee.db'


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()
    connectable = engine_from_config(
        configuration, prefix="sqlalchemy.", poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
