import os
from typing import Optional
from sqlmodel import Field, SQLModel, create_engine

# Define the Link model representing the table in the database
class Link(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    long_url: str = Field(index=True)  # Added index for query performance
    short_code: str = Field(unique=True, index=True) # Added unique and index

# Database setup
# Determine the absolute path for the database file to ensure it's created in the correct location
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sqlite_file_name = os.path.join(BASE_DIR, "database.db")
sqlite_url = f"sqlite:///{sqlite_file_name}"

# Create the engine
# check_same_thread=False is required for SQLite when using multiple threads (e.g., in FastAPI)
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def create_db_and_tables():
    """ Creates the database and tables if they do not exist. """
    SQLModel.metadata.create_all(engine)
