"""
SEC EDGAR Data Collector Module
This module fetches official SEC filings including:
- Form 4 (Insider Trading)
- 13F Filings (Institutional Holdings)
- And other filings that indicate market sentiment

The SEC provides free access to EDGAR data but requires:
1. A proper User-Agent header with your contact info
2. Rate limiting to max 10 requests per second
"""

import requests
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
from bs4 import BeautifulSoup
import json

# Import our configuration
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
from config.config import Config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SECEdgarCollector:
    """
    Collects data from SEC EDGAR database.

    EDGAR (Electronic Data Gathering, Analysis, and Retrieval) is the SEC's
    system for companies to submit required filings.

    Important filings for sentiment analysis:
    - Form 4: Insider trading (when executives buy/sell company stock)
    - 13F: Quarterly reports of institutional investment managers
    - 8-K: Major company events
    - 10-Q/10-K: Quarterly/Annual reports
    """

    def __init__(self):
        """
        Initialize the SEC EDGAR collector.
        Sets up headers and rate limiting.
        """
        # SEC requires a User-Agent header with contact information
        self.headers = {
            'User-Agent': Config.SEC_USER_AGENT,
            'Accept-Encoding': 'gzip, deflate',
            'Host': 'www.sec.gov'
        }

        # Base URLs for SEC EDGAR
        self.base_url = 'https://www.sec.gov'
        self.cik_lookup_url = f'{self.base_url}/cgi-bin/browse-edgar'
        self.submissions_url = f'{self.base_url}/cgi-bin/browse-edgar'

        # Rate limiting: SEC allows max 10 requests per second
        self.min_request_interval = 1.0 / Config.SEC_RATE_LIMIT  # 0.1 seconds
        self.last_request_time = 0

        logger.info("SEC EDGAR collector initialized")

    def _rate_limit(self):
        """
        Enforce rate limiting to comply with SEC requirements.
        Waits if necessary to maintain max 10 requests/second.
        """
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time

        if time_since_last_request < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last_request
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    def _make_request(self, url: str, params: Optional[Dict] = None) -> Optional[requests.Response]:
        """
        Make a rate-limited request to SEC EDGAR.

        Args:
            url: URL to request
            params: Optional query parameters

        Returns:
            Response object or None if request failed
        """
        self._rate_limit()

        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            return None

    def get_company_cik(self, ticker: str) -> Optional[str]:
        """
        Get the CIK (Central Index Key) for a company by ticker symbol.

        CIK is the unique identifier SEC uses for companies.
        For example: Apple (AAPL) has CIK 0000320193

        Args:
            ticker: Stock ticker symbol (e.g., "AAPL")

        Returns:
            CIK string with leading zeros, or None if not found

        Note: This uses the SEC's company tickers JSON endpoint
        """
        try:
            # SEC provides a JSON file mapping tickers to CIKs
            url = f'{self.base_url}/files/company_tickers.json'
            response = self._make_request(url)

            if not response:
                return None

            # Parse the JSON data
            data = response.json()

            # Search for the ticker
            ticker = ticker.upper()
            for entry in data.values():
                if entry['ticker'].upper() == ticker:
                    # CIK needs to be padded with zeros to 10 digits
                    cik = str(entry['cik_str']).zfill(10)
                    logger.info(f"Found CIK for {ticker}: {cik}")
                    return cik

            logger.warning(f"CIK not found for ticker: {ticker}")
            return None

        except Exception as e:
            logger.error(f"Error getting CIK for {ticker}: {e}")
            return None

    def get_recent_filings(
        self,
        ticker: str,
        filing_type: str = "4",
        count: int = 10
    ) -> List[Dict]:
        """
        Get recent filings for a company.

        Args:
            ticker: Stock ticker symbol
            filing_type: Type of filing (e.g., "4" for Form 4, "13F-HR" for 13F)
            count: Number of recent filings to retrieve

        Returns:
            List of filing dictionaries

        Common filing types:
        - "4": Insider trading (Form 4)
        - "13F-HR": Institutional holdings (13F)
        - "8-K": Major events
        - "10-Q": Quarterly report
        - "10-K": Annual report
        """
        # Get the company's CIK first
        cik = self.get_company_cik(ticker)
        if not cik:
            logger.error(f"Cannot get filings: CIK not found for {ticker}")
            return []

        try:
            # Use SEC's submissions endpoint
            url = f'{self.base_url}/cgi-bin/browse-edgar'
            params = {
                'action': 'getcompany',
                'CIK': cik,
                'type': filing_type,
                'dateb': '',  # End date (empty = today)
                'owner': 'include',  # Include insider filings
                'count': count,
                'search_text': ''
            }

            response = self._make_request(url, params=params)
            if not response:
                return []

            # Parse the HTML response
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find the filings table
            filings_table = soup.find('table', {'class': 'tableFile2'})
            if not filings_table:
                logger.warning(f"No filings found for {ticker} (type: {filing_type})")
                return []

            filings = []
            rows = filings_table.find_all('tr')[1:]  # Skip header row

            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 4:
                    filing_data = {
                        'ticker': ticker,
                        'cik': cik,
                        'filing_type': cols[0].text.strip(),
                        'filing_date': cols[3].text.strip(),
                        'description': cols[2].text.strip(),
                    }

                    # Get document link if available
                    link = cols[1].find('a')
                    if link:
                        filing_data['document_link'] = self.base_url + link['href']

                    filings.append(filing_data)

            logger.info(f"Retrieved {len(filings)} {filing_type} filings for {ticker}")
            return filings

        except Exception as e:
            logger.error(f"Error getting filings for {ticker}: {e}")
            return []

    def get_form4_filings(self, ticker: str, count: int = 10) -> List[Dict]:
        """
        Get recent Form 4 (insider trading) filings.

        Form 4 must be filed when company insiders (executives, directors, major
        shareholders) buy or sell company stock.

        Why it matters for sentiment:
        - Insider buying often signals confidence in the company
        - Insider selling might indicate concerns (or just normal portfolio management)

        Args:
            ticker: Stock ticker symbol
            count: Number of recent filings to retrieve

        Returns:
            List of Form 4 filing dictionaries
        """
        return self.get_recent_filings(ticker, filing_type="4", count=count)

    def get_13f_filings(self, ticker: str, count: int = 5) -> List[Dict]:
        """
        Get recent 13F filings for institutional holders.

        13F filings show what stocks institutional investment managers
        (mutual funds, hedge funds, etc.) are holding.

        Why it matters for sentiment:
        - Shows what the "smart money" is investing in
        - Large increases in holdings = bullish sentiment
        - Large decreases = bearish sentiment

        Args:
            ticker: Stock ticker symbol
            count: Number of recent filings to retrieve

        Returns:
            List of 13F filing dictionaries

        Note: 13F filings are quarterly, so you won't see many recent ones
        """
        return self.get_recent_filings(ticker, filing_type="13F-HR", count=count)

    def analyze_insider_sentiment(self, form4_filings: List[Dict]) -> Dict[str, any]:
        """
        Analyze insider trading sentiment from Form 4 filings.

        This is a simplified analysis. A more sophisticated version would
        parse the actual XML documents to get transaction details.

        Args:
            form4_filings: List of Form 4 filings

        Returns:
            Dictionary with sentiment analysis

        Note: This is a basic implementation. For production use, you'd want to
        parse the actual filing documents to get buy/sell details and amounts.
        """
        if not form4_filings:
            return {
                'sentiment': 'neutral',
                'score': 0.0,
                'filing_count': 0,
                'description': 'No recent insider activity'
            }

        # Count recent filings as a proxy for activity level
        recent_count = len(form4_filings)

        # In a real implementation, you would:
        # 1. Parse each Form 4 XML document
        # 2. Extract buy vs sell transactions
        # 3. Calculate net insider buying/selling
        # 4. Weight by transaction size

        # For now, we'll return basic info
        return {
            'sentiment': 'active',  # Just indicates activity level
            'score': min(recent_count / 20.0, 1.0),  # Normalize to 0-1
            'filing_count': recent_count,
            'description': f'{recent_count} insider transaction(s) in recent period',
            'latest_date': form4_filings[0]['filing_date'] if form4_filings else None
        }


# Example usage and testing
if __name__ == "__main__":
    """
    Test the SEC EDGAR collector.
    """
    print("\n=== Testing SEC EDGAR Collector ===\n")

    # Create collector instance
    collector = SECEdgarCollector()

    # Test 1: Get CIK for a company
    print("Test 1: Looking up CIK for AAPL (Apple)")
    print("-" * 60)
    cik = collector.get_company_cik("AAPL")
    print(f"CIK: {cik}\n")

    # Test 2: Get Form 4 filings (insider trading)
    print("Test 2: Getting recent Form 4 filings for AAPL")
    print("-" * 60)
    form4_filings = collector.get_form4_filings("AAPL", count=5)

    if form4_filings:
        print(f"Found {len(form4_filings)} Form 4 filings:\n")
        for i, filing in enumerate(form4_filings[:3], 1):
            print(f"Filing {i}:")
            print(f"  Date: {filing['filing_date']}")
            print(f"  Type: {filing['filing_type']}")
            print(f"  Description: {filing['description'][:80]}...")
            print()

        # Analyze insider sentiment
        sentiment = collector.analyze_insider_sentiment(form4_filings)
        print("Insider Activity Analysis:")
        print(f"  {sentiment['description']}")
        print(f"  Activity Score: {sentiment['score']:.2f}")
    else:
        print("No Form 4 filings found")

    print("\n" + "=" * 60)
    print("Note: To get detailed transaction data (buy/sell amounts),")
    print("you would need to parse the actual XML documents.")
    print("This basic implementation just tracks filing activity.")
