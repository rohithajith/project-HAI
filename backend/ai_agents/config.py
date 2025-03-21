"""
Configuration module for the Hotel AI Assistant.

This module loads environment variables and provides configuration settings
for the application.
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# LLM configuration
LLM_MODEL = os.environ.get("LLM_MODEL", "gpt-4o")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Server configuration
PORT = int(os.environ.get("PORT", 8000))
HOST = os.environ.get("HOST", "0.0.0.0")
DEBUG = os.environ.get("DEBUG", "False").lower() == "true"

# Database configuration
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///hotel_bookings.db")

# CORS configuration
CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*").split(",")

# Logging configuration
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")

# Privacy and consent configuration
DATA_RETENTION_DAYS = int(os.environ.get("DATA_RETENTION_DAYS", 30))
ANONYMIZE_DATA = os.environ.get("ANONYMIZE_DATA", "True").lower() == "true"

# API keys for external services
CAB_BOOKING_API_KEY = os.environ.get("CAB_BOOKING_API_KEY")
ENTERTAINMENT_API_KEY = os.environ.get("ENTERTAINMENT_API_KEY")

# Feature flags
ENABLE_WELLNESS_FEATURES = os.environ.get("ENABLE_WELLNESS_FEATURES", "True").lower() == "true"
ENABLE_ENTERTAINMENT_FEATURES = os.environ.get("ENABLE_ENTERTAINMENT_FEATURES", "True").lower() == "true"
ENABLE_CAB_BOOKING = os.environ.get("ENABLE_CAB_BOOKING", "True").lower() == "true"

def get_config() -> Dict[str, Any]:
    """Get the application configuration as a dictionary.
    
    Returns:
        A dictionary containing all configuration settings
    """
    return {
        "llm": {
            "model": LLM_MODEL,
            "openai_api_key": OPENAI_API_KEY
        },
        "server": {
            "port": PORT,
            "host": HOST,
            "debug": DEBUG
        },
        "database": {
            "url": DATABASE_URL
        },
        "cors": {
            "origins": CORS_ORIGINS
        },
        "logging": {
            "level": LOG_LEVEL
        },
        "privacy": {
            "data_retention_days": DATA_RETENTION_DAYS,
            "anonymize_data": ANONYMIZE_DATA
        },
        "external_services": {
            "cab_booking_api_key": CAB_BOOKING_API_KEY,
            "entertainment_api_key": ENTERTAINMENT_API_KEY
        },
        "features": {
            "wellness": ENABLE_WELLNESS_FEATURES,
            "entertainment": ENABLE_ENTERTAINMENT_FEATURES,
            "cab_booking": ENABLE_CAB_BOOKING
        }
    }