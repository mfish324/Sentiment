"""
Test script to show what free data is actually available.
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from src.data_sources.sec_edgar_collector import SECEdgarCollector

print("\n" + "="*70)
print("TESTING FREE DATA SOURCES")
print("="*70 + "\n")

# Test SEC EDGAR (FREE - No API key needed!)
print("1. SEC EDGAR - Insider Trading (Form 4)")
print("-" * 70)

sec = SECEdgarCollector()
ticker = "AAPL"

print(f"Fetching Form 4 filings for {ticker}...")
filings = sec.get_form4_filings(ticker, count=5)

if filings:
    print(f"\n✅ Found {len(filings)} insider trading filings:\n")
    for i, filing in enumerate(filings, 1):
        print(f"{i}. Date: {filing['filing_date']}")
        print(f"   Type: {filing['filing_type']}")
        print(f"   Link: {filing.get('document_link', 'N/A')[:60]}...")
        print()

    # Analyze sentiment
    sentiment = sec.analyze_insider_sentiment(filings)
    print("Insider Activity Analysis:")
    print(f"  {sentiment['description']}")
    print(f"  Activity Score: {sentiment['score']:.2f}")
else:
    print("❌ No filings found")

print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print("\n✅ FREE and WORKING:")
print("  - SEC EDGAR: Form 4 insider trading filings")
print("  - SEC EDGAR: Filing frequency tracking")
print("  - Sentiment analysis (TextBlob + VADER)")

print("\n❌ NOT AVAILABLE (Free Tier):")
print("  - FMP Institutional Holdings (requires $149/mo Ultimate plan)")
print("  - FMP Insider Trading (requires $59/mo Premium plan)")
print("  - Twitter Search (requires $100/mo Basic plan)")

print("\n💡 RECOMMENDATION:")
print("  Use SEC EDGAR for free insider trading data!")
print("  Or I can add Yahoo Finance for stock prices + top holders (also free)")

print("\n" + "="*70 + "\n")
