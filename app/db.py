from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings

# Connect to your existing PostgreSQL database
engine = create_engine(settings.DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

def get_session():
    """Return a new SQLAlchemy session."""
    return SessionLocal()