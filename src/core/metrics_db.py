# -------------------------------------------------------------
# Defines SQLite schema (requests + responses tables) via SQLAlchemy.
# Handles DB engine creation and initialization.
# Persists latency, cost, and quality metrics for every LLM call.
# -------------------------------------------------------------

from sqlalchemy import (
    create_engine, MetaData, Table, Column, String, Integer, Float, Text, DateTime
)
from sqlalchemy.dialects.sqlite import JSON as SQLITE_JSON
from sqlalchemy.orm import sessionmaker
import datetime as dt
from .config import DB_URL

metadata = MetaData()

requests_table = Table(
    "requests", metadata,
    Column("request_id", String, primary_key=True),
    Column("ts", DateTime, default=dt.datetime.utcnow),
    Column("provider", String),
    Column("model", String),
    Column("prompt_hash", String),
    Column("prompt_len", Integer),
    Column("params", SQLITE_JSON),
    Column("latency_ms", Float),
    Column("status", String),
    Column("error_msg", Text)
)

responses_table = Table(
    "responses", metadata,
    Column("request_id", String, primary_key=True),
    Column("response", Text),
    Column("usage_tokens_in", Integer),
    Column("usage_tokens_out", Integer),
    Column("cost_usd", Float),
    Column("quality_proxy", Float)
)

engine = create_engine(DB_URL, future=True)
SessionLocal = sessionmaker(bind=engine, future=True)

def init_db():
    metadata.create_all(engine)
    print(f"✅ Database initialized at {DB_URL}")

# -------------------------------------------------------------
# Helper functions to insert records into the database tables.
# -------------------------------------------------------------

def insert_request(session, row: dict) -> None:
    session.execute(requests_table.insert().values(**row))

def insert_response(session, row: dict) -> None:
    session.execute(responses_table.insert().values(**row))
