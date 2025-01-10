from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings."""

    PROXYCURL_API_KEY: str
    OPENAI_API_KEY: str
    TAVILY_API_KEY: str

    # Other settings with defaults
    OPENAI_MODEL_NAME: str = "gpt-4o-mini"
    
    # Configure .env file loading
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings."""
    return Settings()


# Create a settings instance to import
settings = get_settings()
