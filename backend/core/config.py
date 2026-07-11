"""
Configuration Loader Module

This module handles loading and managing application configuration.
It provides a centralized interface for accessing configuration values
from environment variables using pydantic-settings for type-safe
configuration management.
"""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """
    Centralized configuration management for the application.
    
    This class loads configuration from environment variables and
    provides type-safe access to configuration values using pydantic's
    BaseSettings for automatic validation and type conversion.
    
    Configuration is automatically loaded from the .env file in the
    project root directory.
    """
    APP_NAME: str = Field(
        default="AutoResearchAI",
        description="Application name"
    )

    APP_VERSION: str = Field(
        default="0.1.0",
        description="Current application version"
    )

    ENVIRONMENT: str = Field(
        default="development",
        description="Application environment"
    )

    OPENROUTER_API_KEY: str = Field(
        ...,
        description="API key for OpenRouter service"
    )
    
    MODEL_NAME: str = Field(
        default="deepseek/deepseek-chat-v3-0324:free",
        description="Default model used by the application"
    )
    
    TEMPERATURE: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Temperature setting for LLM generation"
    )
    
    MAX_TOKENS: int = Field(
        default=4096,
        gt=0,
        description="Maximum tokens for LLM responses"
    )
    
    LOG_LEVEL: str = Field(
        default="INFO",
        description="Logging level for the application"
    )
    
    class Config:
        """
        Pydantic configuration for settings.
        
        Configures the settings class to automatically load from
        environment variables and the .env file.
        """
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


# Singleton instance of settings
settings = Settings()
