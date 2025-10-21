"""
Configuration module for the Sentiment Analysis App.
This file loads environment variables and provides configuration settings.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Get the project root directory (parent of config folder)
PROJECT_ROOT = Path(__file__).parent.parent

# Load environment variables from .env file
load_dotenv(PROJECT_ROOT / 'config' / '.env')


class Config:
    """
    Configuration class that stores all application settings.
    Settings are loaded from environment variables.
    """

    # ==================== Twitter/X API Settings ====================
    TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
    TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET')
    TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
    TWITTER_ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
    TWITTER_BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN')
    TWITTER_RATE_LIMIT = int(os.getenv('TWITTER_RATE_LIMIT', 450))

    # ==================== SEC EDGAR Settings ====================
    SEC_USER_AGENT = os.getenv('SEC_USER_AGENT', 'SentimentApp contact@example.com')
    SEC_RATE_LIMIT = int(os.getenv('SEC_RATE_LIMIT', 10))
    SEC_BASE_URL = 'https://www.sec.gov'

    # ==================== Database Settings ====================
    DATABASE_PATH = PROJECT_ROOT / 'data' / 'sentiment.db'

    # ==================== Analysis Settings ====================
    SENTIMENT_THRESHOLD_POSITIVE = float(os.getenv('SENTIMENT_THRESHOLD_POSITIVE', 0.05))
    SENTIMENT_THRESHOLD_NEGATIVE = float(os.getenv('SENTIMENT_THRESHOLD_NEGATIVE', -0.05))

    # ==================== Logging Settings ====================
    LOG_DIR = PROJECT_ROOT / 'logs'
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

    # ==================== Data Directory ====================
    DATA_DIR = PROJECT_ROOT / 'data'

    @classmethod
    def validate(cls):
        """
        Validates that required configuration values are set.
        Raises ValueError if any required settings are missing.
        """
        required_settings = []

        # Check Twitter credentials (only if you're using Twitter)
        if not cls.TWITTER_BEARER_TOKEN:
            required_settings.append('TWITTER_BEARER_TOKEN')

        # Check SEC user agent
        if 'example.com' in cls.SEC_USER_AGENT:
            required_settings.append('SEC_USER_AGENT (must use your real email)')

        if required_settings:
            raise ValueError(
                f"Missing required configuration: {', '.join(required_settings)}\n"
                f"Please copy config/.env.example to config/.env and fill in your values."
            )

    @classmethod
    def create_directories(cls):
        """Creates necessary directories if they don't exist."""
        cls.LOG_DIR.mkdir(parents=True, exist_ok=True)
        cls.DATA_DIR.mkdir(parents=True, exist_ok=True)


# Create directories on import
Config.create_directories()
