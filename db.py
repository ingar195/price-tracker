"""
Database connection setup.

engine: knows *how* to talk to the DB file (sqlite:///pricetracker.db means
        a local file called pricetracker.db in this folder).
Session: your actual "conversation" with the DB — you open one, do work
        (add/query objects), commit, then close it.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base

DATABASE_URL = "sqlite:///pricetracker.db"

engine = create_engine(DATABASE_URL, echo=False)  # set echo=True to see generated SQL
SessionLocal = sessionmaker(bind=engine)


def init_db() -> None:
    """Create all tables that don't exist yet. Safe to call every run."""
    Base.metadata.create_all(engine)
