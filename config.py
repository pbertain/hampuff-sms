#!/usr/bin/env python3
"""
Configuration settings for the Hampuff SMS Web Service.
"""

import os


class Config:
    """Base configuration class."""
    
    # Flask settings
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key-change-in-production"
    DEBUG = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    
    # Server settings
    HOST = os.environ.get("HOST", "0.0.0.0")
    PORT = int(os.environ.get("PORT", 15015))
    
    # Twilio settings (for future use if needed)
    TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID", "put_your_account_sid_here")
    TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN", "put_your_auth_token_here")
    
    # Application settings
    CONSENT_MESSAGE = "Your SMS request provides consent to send the reply."
    AIRPUFF_MESSAGE = (
        "Wrong number. That might be an airport so please text Airpuff "
        "at sms://+1-802-247-7833 / [802-AIR-PUFF]"
    )
    DEFAULT_WRONG_NUMBER_MESSAGE = "Wrong number. Please waste someone else's time."
    
    # Database settings
    REGISTRATION_DB_PATH = os.environ.get("REGISTRATION_DB_PATH", "/opt/hampuff-data/registrations.db")
    
    # Logging
    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    LOG_LEVEL = "DEBUG"


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    LOG_LEVEL = "WARNING"


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True
    LOG_LEVEL = "DEBUG"


# Configuration mapping
config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig
}
