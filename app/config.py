from dataclasses import dataclass

@dataclass
class Settings:
    DATABASE_URL: str = "postgresql+psycopg2://postgres:admin@localhost:5432/expense_tracker"
    EXPORT_DIR: str = "build/exports"
    LOG_LEVEL: str = "INFO"

settings = Settings()