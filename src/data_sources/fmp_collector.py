"""
Financial Modeling Prep (FMP) API Collector Module
This module fetches institutional and mutual fund holdings data from FMP.

FMP provides:
- Institutional holdings (13F filings)
- Mutual fund holdings
- Insider trading data
- Stock ownership data

Get your free API key at: https://site.financialmodelingprep.com/developer/docs
Free tier: 250 requests/day
"""

import requests
import time
from datetime import datetime
from typing import List, Dict, Optional
import logging

# Import our configuration
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
from config.config import Config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FMPCollector:
    """
    Collects financial data from Financial Modeling Prep API.

    This includes:
    - Institutional holders (who owns the stock)
    - Mutual fund holders
    - Insider trading transactions
    - Stock ownership changes over time
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the FMP collector.

        Args:
            api_key: FMP API key (uses config if not provided)
        """
        self.api_key = api_key or Config.FMP_API_KEY
        self.base_url = 'https://financialmodelingprep.com/api/v3'
        self.base_url_v4 = 'https://financialmodelingprep.com/api/v4'

        # Rate limiting for free tier (250 requests/day)
        self.requests_per_day = 250
        self.min_request_interval = 0.5  # 0.5 seconds between requests
        self.last_request_time = 0

        logger.info("FMP API collector initialized")

    def _rate_limit(self):
        """Enforce rate limiting between API calls."""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time

        if time_since_last_request < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last_request
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """
        Make a rate-limited request to FMP API.

        Args:
            endpoint: API endpoint (e.g., '/institutional-holder/AAPL')
            params: Optional query parameters

        Returns:
            JSON response or None if request failed
        """
        self._rate_limit()

        # Add API key to params
        if params is None:
            params = {}
        params['apikey'] = self.api_key

        # Determine base URL
        if endpoint.startswith('/v4/'):
            url = self.base_url_v4 + endpoint.replace('/v4', '')
        else:
            url = self.base_url + endpoint

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"FMP API request failed: {e}")
            return None

    def get_institutional_holders(self, ticker: str) -> List[Dict]:
        """
        Get institutional holders for a stock.

        Institutional holders are large organizations like:
        - Mutual funds
        - Pension funds
        - Hedge funds
        - Investment firms

        Args:
            ticker: Stock ticker symbol (e.g., "AAPL")

        Returns:
            List of institutional holder dictionaries

        Example result:
            {
                'holder': 'Vanguard Group Inc',
                'shares': 1234567890,
                'dateReported': '2024-03-31',
                'change': 5000000,
                'percentHeld': 7.5
            }
        """
        logger.info(f"Fetching institutional holders for {ticker}")

        endpoint = f'/institutional-holder/{ticker.upper()}'
        data = self._make_request(endpoint)

        if not data:
            logger.warning(f"No institutional holder data found for {ticker}")
            return []

        # Add ticker to each record
        for holder in data:
            holder['ticker'] = ticker.upper()

        logger.info(f"Retrieved {len(data)} institutional holders for {ticker}")
        return data

    def get_mutual_fund_holders(self, ticker: str) -> List[Dict]:
        """
        Get mutual fund holders for a stock.

        Args:
            ticker: Stock ticker symbol

        Returns:
            List of mutual fund holder dictionaries

        Example result:
            {
                'holder': 'Vanguard Total Stock Market Index Fund',
                'shares': 50000000,
                'dateReported': '2024-03-31',
                'change': 1000000,
                'weightPercent': 2.5
            }
        """
        logger.info(f"Fetching mutual fund holders for {ticker}")

        endpoint = f'/mutual-fund-holder/{ticker.upper()}'
        data = self._make_request(endpoint)

        if not data:
            logger.warning(f"No mutual fund holder data found for {ticker}")
            return []

        # Add ticker to each record
        for holder in data:
            holder['ticker'] = ticker.upper()

        logger.info(f"Retrieved {len(data)} mutual fund holders for {ticker}")
        return data

    def get_insider_trades(self, ticker: str) -> List[Dict]:
        """
        Get insider trading transactions for a stock.

        Similar to SEC Form 4, but from FMP's database.
        Easier to parse than SEC's XML format.

        Args:
            ticker: Stock ticker symbol

        Returns:
            List of insider trading dictionaries

        Example result:
            {
                'symbol': 'AAPL',
                'filingDate': '2024-01-15',
                'transactionDate': '2024-01-10',
                'reportingName': 'COOK TIMOTHY D',
                'transactionType': 'P-Purchase',
                'securitiesOwned': 100000,
                'securitiesTransacted': 5000,
                'price': 185.50
            }
        """
        logger.info(f"Fetching insider trades for {ticker}")

        endpoint = f'/v4/insider-trading'
        params = {'symbol': ticker.upper()}
        data = self._make_request(endpoint, params)

        if not data:
            logger.warning(f"No insider trading data found for {ticker}")
            return []

        logger.info(f"Retrieved {len(data)} insider trades for {ticker}")
        return data

    def get_stock_ownership(self, ticker: str) -> Dict:
        """
        Get overall stock ownership breakdown.

        Shows who owns the stock:
        - Institutions
        - Insiders
        - Public float

        Args:
            ticker: Stock ticker symbol

        Returns:
            Dictionary with ownership percentages
        """
        logger.info(f"Fetching stock ownership for {ticker}")

        endpoint = f'/v4/institutional-ownership/symbol-ownership'
        params = {'symbol': ticker.upper()}
        data = self._make_request(endpoint, params)

        if not data or len(data) == 0:
            logger.warning(f"No ownership data found for {ticker}")
            return {}

        # Return the most recent data
        return data[0] if isinstance(data, list) else data

    def analyze_institutional_sentiment(self, ticker: str) -> Dict:
        """
        Analyze institutional sentiment based on ownership changes.

        Positive sentiment indicators:
        - Increasing number of institutional holders
        - Large institutions increasing positions
        - New major institutions taking positions

        Args:
            ticker: Stock ticker symbol

        Returns:
            Dictionary with sentiment analysis
        """
        holders = self.get_institutional_holders(ticker)

        if not holders:
            return {
                'sentiment': 'unknown',
                'score': 0.0,
                'holder_count': 0,
                'description': 'No institutional holder data available'
            }

        # Count holders with increasing vs decreasing positions
        increasing = sum(1 for h in holders if h.get('change', 0) > 0)
        decreasing = sum(1 for h in holders if h.get('change', 0) < 0)
        total = len(holders)

        # Calculate sentiment score
        if total > 0:
            score = (increasing - decreasing) / total
        else:
            score = 0.0

        # Determine sentiment label
        if score > 0.3:
            sentiment = 'bullish'
        elif score < -0.3:
            sentiment = 'bearish'
        else:
            sentiment = 'neutral'

        return {
            'sentiment': sentiment,
            'score': score,
            'holder_count': total,
            'increasing_positions': increasing,
            'decreasing_positions': decreasing,
            'description': f'{increasing} institutions increased, {decreasing} decreased positions'
        }

    def analyze_insider_sentiment(self, ticker: str, days: int = 90) -> Dict:
        """
        Analyze insider sentiment based on recent trades.

        Args:
            ticker: Stock ticker symbol
            days: Number of days to look back

        Returns:
            Dictionary with insider sentiment analysis
        """
        trades = self.get_insider_trades(ticker)

        if not trades:
            return {
                'sentiment': 'unknown',
                'score': 0.0,
                'trade_count': 0,
                'description': 'No insider trading data available'
            }

        # Filter to recent trades (last N days)
        cutoff_date = datetime.now()
        from dateutil.relativedelta import relativedelta
        cutoff_date = cutoff_date - relativedelta(days=days)

        recent_trades = []
        for trade in trades:
            try:
                trade_date = datetime.strptime(trade['transactionDate'], '%Y-%m-%d')
                if trade_date >= cutoff_date:
                    recent_trades.append(trade)
            except:
                continue

        if not recent_trades:
            return {
                'sentiment': 'neutral',
                'score': 0.0,
                'trade_count': 0,
                'description': f'No insider trades in last {days} days'
            }

        # Count buys vs sells
        buys = sum(1 for t in recent_trades if 'P' in t.get('transactionType', ''))
        sells = sum(1 for t in recent_trades if 'S' in t.get('transactionType', ''))

        # Calculate sentiment
        total = buys + sells
        if total > 0:
            score = (buys - sells) / total
        else:
            score = 0.0

        if score > 0.2:
            sentiment = 'bullish'
        elif score < -0.2:
            sentiment = 'bearish'
        else:
            sentiment = 'neutral'

        return {
            'sentiment': sentiment,
            'score': score,
            'trade_count': total,
            'buys': buys,
            'sells': sells,
            'description': f'{buys} insider buys, {sells} sells in last {days} days'
        }


# Example usage and testing
if __name__ == "__main__":
    """
    Test the FMP collector.
    Note: You need an FMP API key to run this test.
    """
    print("\n=== Testing FMP API Collector ===\n")

    # Check if API key is configured
    try:
        api_key = Config.FMP_API_KEY
        if not api_key or api_key == 'your_fmp_api_key_here':
            print("⚠️  FMP API key not configured!")
            print("Get your free API key at: https://site.financialmodelingprep.com/developer/docs")
            print("Then add it to config/.env as: FMP_API_KEY=your_key_here")
            exit(1)
    except AttributeError:
        print("⚠️  FMP_API_KEY not found in config!")
        print("Add it to config/.env: FMP_API_KEY=your_key_here")
        exit(1)

    # Create collector instance
    collector = FMPCollector()

    # Test 1: Get institutional holders
    print("Test 1: Getting institutional holders for AAPL")
    print("-" * 60)
    holders = collector.get_institutional_holders("AAPL")

    if holders:
        print(f"Found {len(holders)} institutional holders:\n")
        for i, holder in enumerate(holders[:5], 1):
            print(f"{i}. {holder.get('holder', 'Unknown')}")
            print(f"   Shares: {holder.get('shares', 0):,}")
            print(f"   Change: {holder.get('change', 0):,}")
            print(f"   Date: {holder.get('dateReported', 'N/A')}")
            print()
    else:
        print("No institutional holder data found")

    print()

    # Test 2: Analyze institutional sentiment
    print("Test 2: Analyzing institutional sentiment for AAPL")
    print("-" * 60)
    inst_sentiment = collector.analyze_institutional_sentiment("AAPL")
    print(f"Sentiment: {inst_sentiment['sentiment']}")
    print(f"Score: {inst_sentiment['score']:.3f}")
    print(f"Description: {inst_sentiment['description']}")

    print()

    # Test 3: Get insider trades
    print("Test 3: Getting insider trades for AAPL")
    print("-" * 60)
    trades = collector.get_insider_trades("AAPL")

    if trades:
        print(f"Found {len(trades)} insider trades:\n")
        for i, trade in enumerate(trades[:5], 1):
            print(f"{i}. {trade.get('reportingName', 'Unknown')}")
            print(f"   Type: {trade.get('transactionType', 'N/A')}")
            print(f"   Shares: {trade.get('securitiesTransacted', 0):,}")
            print(f"   Date: {trade.get('transactionDate', 'N/A')}")
            print()

        # Analyze insider sentiment
        insider_sentiment = collector.analyze_insider_sentiment("AAPL", days=90)
        print("Insider Sentiment Analysis:")
        print(f"  Sentiment: {insider_sentiment['sentiment']}")
        print(f"  Score: {insider_sentiment['score']:.3f}")
        print(f"  {insider_sentiment['description']}")
    else:
        print("No insider trading data found")

    print("\n" + "="*60)
    print("FMP API test complete!")
