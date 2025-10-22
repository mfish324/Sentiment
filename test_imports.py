"""
Test script to verify all required imports work.
Run this to diagnose import issues.
"""

import sys
print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")
print(f"Python path: {sys.path}\n")

print("Testing imports...")
print("-" * 60)

# Test each import
imports = [
    ("dotenv", "from dotenv import load_dotenv"),
    ("requests", "import requests"),
    ("tweepy", "import tweepy"),
    ("textblob", "from textblob import TextBlob"),
    ("vaderSentiment", "from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer"),
    ("beautifulsoup4", "from bs4 import BeautifulSoup"),
    ("pytz", "import pytz"),
    ("dateutil", "from dateutil import parser"),
]

failed = []
for name, import_statement in imports:
    try:
        exec(import_statement)
        print(f"✓ {name:20s} - OK")
    except ImportError as e:
        print(f"✗ {name:20s} - FAILED: {e}")
        failed.append(name)

print("-" * 60)
if failed:
    print(f"\n❌ {len(failed)} package(s) failed to import:")
    for name in failed:
        print(f"   - {name}")
    print("\nTo install missing packages, run:")
    print("   pip install python-dotenv requests tweepy textblob vaderSentiment beautifulsoup4 pytz python-dateutil")
else:
    print("\n✓ All packages imported successfully!")
    print("\nYou can now run:")
    print("   python src/main.py --ticker AAPL --tweets 10")
