import pytest
from sqlalchemy import create_engine
from app.config import settings  # import your Settings dataclass
from app.db import SessionLocal
from app.models import Account

def test_database_connection():
    engine = create_engine(settings.DATABASE_URL)
    try:
        with engine.connect() as conn:
            assert conn.closed == False
            print("✅ Connected successfully to:", conn)
    except Exception as e:
        pytest.fail(f"❌ Connection failed: {e}")

def get_accounts():
    with SessionLocal() as session:
        return session.query(Account).all()