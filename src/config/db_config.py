from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class DBSettings(BaseSettings):
    """Параметры подключения к PostgreSQL из .env."""

    model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", extra="ignore")

    DB_URL: str

    @property
    def DATABASE_URL(self) -> str | None:
        if self.DB_URL.startswith("sqlite"):
            return f"sqlite+aiosqlite:///{BASE_DIR}/my_database.db"
        return None


db_settings = DBSettings()
