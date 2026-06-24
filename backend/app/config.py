from functools import lru_cache
from pathlib import Path
from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "Enterprise Calculation Workspace"
    database_url: str = "sqlite:///./external_calculator.db"
    engine_version: str = "0.1.0"
    frontend_dist: Path = Path(__file__).resolve().parents[2] / "frontend" / "dist"


@lru_cache
def get_settings() -> Settings:
    return Settings()
