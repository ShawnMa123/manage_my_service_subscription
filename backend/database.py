import os
import logging
from sqlmodel import create_engine, SQLModel, Session
from models import Subscription, Setting

logger = logging.getLogger(__name__)

# Get the project root directory (parent of backend folder)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
database_path = os.path.join(project_root, "data", "subscription.db")
database_url = os.getenv("DATABASE_URL", f"sqlite:///{database_path}")

# Create engine with optimized settings for SQLite
engine = create_engine(
    database_url,
    echo=False,  # Disable SQL logging in production for performance
    pool_size=20,  # Connection pool size
    max_overflow=30,  # Additional connections beyond pool_size
    pool_pre_ping=True,  # Verify connections before use
    pool_recycle=3600,  # Recycle connections after 1 hour
    connect_args={
        "check_same_thread": False,  # Allow SQLite to be used across threads
        "timeout": 30,  # Connection timeout
        "pragma_params": {
            "journal_mode": "WAL",  # Write-Ahead Logging for better concurrency
            "synchronous": "NORMAL",  # Balance between safety and performance
            "cache_size": -64000,  # 64MB cache
            "temp_store": "MEMORY",  # Store temporary tables in memory
            "mmap_size": 268435456,  # 256MB memory-mapped I/O
        }
    }
)


def create_db_and_tables():
    """Create database tables and ensure data directory exists"""
    try:
        # Ensure data directory exists
        os.makedirs(os.path.dirname(database_path), exist_ok=True)

        # Create all tables
        SQLModel.metadata.create_all(engine)
        logger.info(f"Database initialized at: {database_path}")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise


def get_session():
    """Get database session with proper error handling"""
    session = Session(engine)
    try:
        yield session
        session.commit()
    except Exception as e:
        logger.error(f"Database session error: {e}")
        session.rollback()
        raise
    finally:
        session.close()