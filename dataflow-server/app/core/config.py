from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=str(Path(__file__).resolve().parents[2] / ".env"))
    
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    
settings = Settings()

def get_database_url() -> str:
    return (
        f"postgresql+asyncpg://"
        f"{settings.POSTGRES_USER}:"
        f"{settings.POSTGRES_PASSWORD}@"
        f"{settings.POSTGRES_HOST}:"
        f"{settings.POSTGRES_PORT}/"
        f"{settings.POSTGRES_DB}"
    )