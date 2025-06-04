"""
Configuration module using Pydantic Settings.
This allows environment variables to override defaults.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
import pytz


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application settings
    app_name: str = "Fitness Studio Booking API"
    debug: bool = True
    
    # Database settings
    database_url: str = "sqlite:///./fitness_booking.db"
    
    # Timezone settings - IST (Indian Standard Time)
    timezone: str = "Asia/Kolkata"
    
    # API settings
    api_v1_prefix: str = "/api/v1"
    
    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    """
    Create settings instance with caching.
    The @lru_cache decorator ensures we create only one instance.
    """
    return Settings()


# Create a global settings instance
settings = get_settings()

# Create timezone object for IST
IST = pytz.timezone(settings.timezone)