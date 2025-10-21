"""
Quick Setup Script
Run this after installing requirements to set up the project.
"""

import os
import sys
from pathlib import Path
import shutil

def main():
    """Set up the project for first-time use."""
    print("=" * 70)
    print("Stock Market Sentiment Analysis App - Setup")
    print("=" * 70)
    print()

    project_root = Path(__file__).parent

    # Step 1: Create .env file if it doesn't exist
    env_file = project_root / 'config' / '.env'
    env_example = project_root / 'config' / '.env.example'

    if not env_file.exists():
        print("✓ Creating config/.env file...")
        shutil.copy(env_example, env_file)
        print("  Created config/.env from template")
        print("  ⚠️  IMPORTANT: Edit config/.env and add your API keys!")
    else:
        print("✓ config/.env already exists")

    print()

    # Step 2: Create necessary directories
    print("✓ Creating data directories...")
    (project_root / 'data').mkdir(exist_ok=True)
    (project_root / 'logs').mkdir(exist_ok=True)
    print("  Created data/ and logs/ directories")
    print()

    # Step 3: Download NLTK data for TextBlob
    print("✓ Downloading required NLTK data for sentiment analysis...")
    try:
        import nltk
        nltk.download('brown', quiet=True)
        nltk.download('punkt', quiet=True)
        print("  Downloaded NLTK data successfully")
    except Exception as e:
        print(f"  ⚠️  Warning: Could not download NLTK data: {e}")
        print("  You may need to run: python -c \"import nltk; nltk.download('brown'); nltk.download('punkt')\"")

    print()

    # Step 4: Test imports
    print("✓ Testing imports...")
    try:
        import tweepy
        import textblob
        import vaderSentiment
        import pandas
        import matplotlib
        import requests
        import bs4
        print("  All required packages are installed")
    except ImportError as e:
        print(f"  ⚠️  Warning: Missing package: {e}")
        print("  Run: pip install -r requirements.txt")

    print()
    print("=" * 70)
    print("Setup Complete!")
    print("=" * 70)
    print()
    print("Next steps:")
    print("1. Edit config/.env and add your Twitter API credentials")
    print("2. Update SEC_USER_AGENT with your email address")
    print("3. Run: python src/main.py --ticker AAPL --tweets 10")
    print()
    print("For detailed instructions, see README.md")
    print()


if __name__ == "__main__":
    main()
