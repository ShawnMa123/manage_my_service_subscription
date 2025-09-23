import os
from sqlmodel import create_engine, SQLModel, Session
from models import Subscription, Setting

database_url = os.getenv("DATABASE_URL", "sqlite:///./data/database.db")
engine = create_engine(database_url, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session