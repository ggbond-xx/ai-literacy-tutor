from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Literacy Tutor API"
    app_version: str = "0.1.0"
    api_prefix: str = "/api"
    secret_key: str = "change-this-secret-key"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 120
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])

    mysql_host: str = "127.0.0.1"
    mysql_port: int = 3306
    mysql_user: str = "root"
    mysql_password: str = "root"
    mysql_db: str = "ai_literacy_tutor"
    database_url: str | None = None

    neo4j_uri: str = "bolt://127.0.0.1:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "password"
    neo4j_database: str = "neo4j"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

    @property
    def sqlalchemy_database_uri(self) -> str:
        return (
            f"mysql+pymysql://{self.mysql_user}:{self.mysql_password}"
            f"@{self.mysql_host}:{self.mysql_port}/{self.mysql_db}?charset=utf8mb4"
        )

    @property
    def sqlite_fallback_uri(self) -> str:
        backend_dir = Path(__file__).resolve().parents[2]
        return f"sqlite:///{backend_dir / 'storage' / 'dev_fallback.db'}"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
