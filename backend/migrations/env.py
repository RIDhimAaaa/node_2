from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool, create_engine
from alembic import context
from dotenv import load_dotenv
import os
import sys
from sqlalchemy.ext.declarative import declarative_base

# Add the backend directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

# Import Base directly without going through config
from sqlalchemy import Column, String, DateTime, Text, Boolean, ForeignKey, Table, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

# Create the base class for SQLAlchemy models
Base = declarative_base()

# Re-define models here to avoid config import issues
class Profile(Base):
    __tablename__ = "profiles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, index=True, nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    bio = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Tracker(Base):
    __tablename__ = "trackers"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey('profiles.id'), nullable=False)
    name = Column(String, nullable=False)
    application_id = Column(String, nullable=False)
    last_status = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def get_database_url():
    """Get the correct database URL for migrations"""
    # Use direct connection for Alembic migrations
    database_url = os.getenv("DATABASE_DIRECT_URL")
    if not database_url:
        # Fallback to regular DATABASE_URL if direct URL not set
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            raise ValueError("DATABASE_DIRECT_URL or DATABASE_URL environment variable is required for migrations")
    
    # Convert asyncpg URLs to psycopg2 for Alembic
    if "postgresql+asyncpg://" in database_url:
        database_url = database_url.replace("postgresql+asyncpg://", "postgresql://")
    
    return database_url

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    database_url = get_database_url()
    
    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_schemas=True,
        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    database_url = get_database_url()
    
    # Create engine specifically for migrations
    connectable = create_engine(database_url)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_schemas=True,
            include_object=include_object
        )

        with context.begin_transaction():
            context.run_migrations()

def include_object(object, name, type_, reflected, compare_to):
    supabase_schemas = {'auth', 'storage', 'realtime', 'vault', 'supabase_functions', 'extensions', 'graphql', 'graphql_public', 'pgsodium', 'pgsodium_masks'}
    
    if hasattr(object, 'schema') and object.schema in supabase_schemas:
        return False
    
    supabase_tables = {'schema_migrations', 'supabase_migrations'}
    if type_ == "table" and name in supabase_tables:
        return False
    
    return True

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()