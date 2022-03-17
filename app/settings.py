import functools
import pydantic
import pydantic.networks

from typing import Optional

class Settings(pydantic.BaseSettings):
    """
    Application settings
    """
    
    testing: bool = False
    google_client_id: Optional[str] = None
    google_client_secret: Optional[str] = None
    database_url: Optional[str] = None #"postgresql+asyncpg://localhost/./test.db"
    session_secret_key: Optional[str] = 'not-secret'
    jwt_secret: Optional[str] = 'not-secret'
    jwt_lifetime_seconds: Optional[int] = 3600

@functools.lru_cache()
def get_settings() -> Settings:
    """
    Get settings
    """
    return Settings()  # Reads variables from environment