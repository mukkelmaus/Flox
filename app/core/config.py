"""
Settings for the OneTask API.

This module defines and loads application settings from environment variables.
"""

import os
import secrets
from typing import Any, Dict, List, Optional, Union

from dotenv import load_dotenv
from pydantic import AnyHttpUrl, EmailStr, HttpUrl, PostgresDsn, field_validator
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8

    # CORS configuration
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Database configuration with flexible connection options
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "localhost")
        POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
        POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
        POSTGRES_DB: str = os.getenv("POSTGRES_DB", "onetask")
        POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
        DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"

    # JWT configuration
    ALGORITHM: str = "HS256"

    # Redis configuration
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost") 
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD")
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))

    # Email configuration
    EMAILS_ENABLED: bool = False
    SMTP_TLS: bool = True
    SMTP_PORT: Optional[int] = None
    SMTP_HOST: Optional[str] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[EmailStr] = None
    EMAILS_FROM_NAME: Optional[str] = None

    @field_validator("EMAILS_ENABLED", mode="before")
    def get_emails_enabled(cls, v: bool, info) -> bool:
        values = info.data
        return bool(
            values.get("SMTP_HOST")
            and values.get("SMTP_PORT")
            and values.get("EMAILS_FROM_EMAIL")
        )

    # OpenAI API configuration
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    ENABLE_AI_FEATURES: bool = os.getenv("ENABLE_AI_FEATURES", "true").lower() == "true"

    # Integration configuration
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    TODOIST_CLIENT_ID: Optional[str] = None
    TODOIST_CLIENT_SECRET: Optional[str] = None
    GITHUB_CLIENT_ID: Optional[str] = None
    GITHUB_CLIENT_SECRET: Optional[str] = None

    # Stripe configuration
    STRIPE_SECRET_KEY: Optional[str] = os.getenv("STRIPE_SECRET_KEY")
    STRIPE_PUBLISHABLE_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None

    # Admin user
    FIRST_SUPERUSER: Optional[str] = "admin"
    FIRST_SUPERUSER_EMAIL: Optional[EmailStr] = "admin@example.com"
    FIRST_SUPERUSER_PASSWORD: Optional[str] = "admin"

    # Application settings
    PROJECT_NAME: str = "Floxari API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Task management API with AI capabilities"
    SERVER_HOST: str = os.getenv("SERVER_HOST", "https://floxari.replit.app")
    DOCS_URL: str = os.getenv("DOCS_URL", "https://floxari.replit.app/docs")
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 5000))
    
    # Core API features
    ENABLE_AI: bool = os.getenv("ENABLE_AI", "false").lower() == "true"
    ENABLE_WEBSOCKETS: bool = os.getenv("ENABLE_WEBSOCKETS", "true").lower() == "true"
    MAX_TASKS_PER_USER: int = int(os.getenv("MAX_TASKS_PER_USER", "1000"))

    # Deployment settings
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = ENVIRONMENT == "development"

    model_config = {
        "case_sensitive": True
    }


settings = Settings()