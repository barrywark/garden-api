import pydantic
import functools

from typing import Optional
from starlette.config import Config

class _Settings(pydantic.BaseSettings):
    google_client_id: Optional[str] = None
    google_client_secret: Optional[str] = None
    database_url: Optional[pydantic.networks.PostgresDsn] = None
    session_secret_key: Optional[str] = 'not-secret'

@functools.lru_cache()
def get_settings() -> _Settings:
    return _Settings()  # Reads variables from environment


_env_conf = Config(".env")

def get_env_config() -> Config:
    return _env_conf