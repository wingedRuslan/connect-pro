from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings."""

    OPENAI_API_KEY: str
    PROXYCURL_API_KEY: str
    TAVILY_API_KEY: str

    # Other settings with defaults
    OPENAI_MODEL_NAME: str = "gpt-4o-mini"

    # Linkedin Credentials (for Selenium)
    LINKEDIN_USERNAME: str
    LINKEDIN_PASSWORD: str
    
    # Configure .env file loading
    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore"
    )


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings."""
    return Settings()


# Create a settings instance to import
settings = get_settings()
