import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

load_dotenv()

DEFAULT_DB_PATH = "sqlite:///./iceberg.db"
DB_PATH = os.getenv("DB_PATH", DEFAULT_DB_PATH)

if DB_PATH.startswith("sqlite."):
    DB_PATH = DEFAULT_DB_PATH

engine = create_engine(DB_PATH, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()
