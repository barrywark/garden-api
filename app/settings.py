from functools import lru_cache
from typing import Optional

from pydantic import BaseSettings, PostgresDsn

class _Settings(BaseSettings):
    google_client_id: Optional[str] = None
    google_client_secret: Optional[str] = None
    database_url: Optional[PostgresDsn] = None



@lru_cache()
def get_settings() -> _Settings:
    return _Settings()  # Reads variables from environment