import os
from sqlmodel import create_engine, SQLModel, Session
from models import Subscription, Setting

# Get the project root directory (parent of backend folder)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
database_path = os.path.join(project_root, "data", "subscription.db")
database_url = os.getenv("DATABASE_URL", f"sqlite:///{database_path}")
engine = create_engine(database_url, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session