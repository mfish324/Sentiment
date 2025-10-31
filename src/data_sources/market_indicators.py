"""
Market Sentiment Indicators Module
Collects and analyzes broad market sentiment indicators using FREE data sources.

This module tracks:
1. VIX (Volatility Index) - Fear gauge
2. Advance/Decline Line - Market breadth
3. Put/Call Ratio - Options sentiment
4. Fear & Greed Index - Composite sentiment
5. Market breadth indicators

All data sources are FREE and don't require paid subscriptions!
"""

import yfinance as yf
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
import pandas as pd

# Import configuration
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))
from config.config import Config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MarketIndicators:
    """
    Collects free market sentiment indicators.

    All indicators are fetched from free sources:
    - yfinance (Yahoo Finance) - FREE, no API key
    - FRED API - FREE, but can benefit from API key
    - Alternative Data (free) - Various free sources
    """

    def __init__(self):
        """Initialize the market indicators collector."""
        self.session = requests.Session()
        logger.info("Market indicators collector initialized")

    # ==================== VIX (Volatility Index) ====================

    def get_vix(self, period: str = "1mo") -> Dict:
        """
        Get VIX (CBOE Volatility Index) data.

        The VIX measures market fear/volatility:
        - VIX < 15: Low fear, complacent market
        - VIX 15-25: Normal market conditions
        - VIX 25-35: Elevated fear, uncertainty
        - VIX > 35: Extreme fear, potential panic

        Args:
            period: Time period (1d, 5d, 1mo, 3mo, 1y, etc.)

        Returns:
            Dictionary with VIX data and analysis

        Source: Yahoo Finance (FREE, no API key needed)
        """
        try:
            logger.info(f"Fetching VIX data for period: {period}")

            # Fetch VIX using yfinance
            vix = yf.Ticker("^VIX")
            hist = vix.history(period=period)

            if hist.empty:
                logger.warning("No VIX data retrieved")
                return {}

            # Get current and historical values
            current_vix = hist['Close'].iloc[-1]
            avg_vix = hist['Close'].mean()
            max_vix = hist['Close'].max()
            min_vix = hist['Close'].min()

            # Calculate sentiment based on VIX level
            if current_vix < 15:
                sentiment = "complacent"
                score = 0.5  # Neutral to bullish
                description = "Low volatility - market is calm"
            elif current_vix < 25:
                sentiment = "neutral"
                score = 0.0
                description = "Normal volatility levels"
            elif current_vix < 35:
                sentiment = "fearful"
                score = -0.4
                description = "Elevated volatility - increased fear"
            else:
                sentiment = "panic"
                score = -0.8
                description = "Extreme volatility - market panic"

            return {
                'current_vix': float(current_vix),
                'avg_vix': float(avg_vix),
                'max_vix': float(max_vix),
                'min_vix': float(min_vix),
                'sentiment': sentiment,
                'score': score,
                'description': description,
                'timestamp': datetime.now()
            }

        except Exception as e:
            logger.error(f"Error fetching VIX data: {e}")
            return {}

    # ==================== Advance/Decline Line ====================

    def get_advance_decline_line(self, period: str = "1mo") -> Dict:
        """
        Calculate Advance/Decline Line for market breadth.

        The A/D line measures how many stocks are advancing vs declining:
        - Rising A/D line: Broad market strength (bullish)
        - Falling A/D line: Broad market weakness (bearish)
        - Divergence from index: Warning sign

        Args:
            period: Time period to analyze

        Returns:
            Dictionary with A/D line data and analysis

        Source: Yahoo Finance (NYSE and NASDAQ A/D data)
        Tickers: ^ISSU (NYSE), ^ISSQ (NASDAQ)
        """
        try:
            logger.info(f"Fetching Advance/Decline data for period: {period}")

            # Yahoo Finance provides A/D data for major exchanges
            # ^ISSU = NYSE Advance/Decline/Unchanged
            # ^ISSQ = NASDAQ Advance/Decline/Unchanged

            nyse_ad = yf.Ticker("^ISSU")
            nasdaq_ad = yf.Ticker("^ISSQ")

            nyse_hist = nyse_ad.history(period=period)
            nasdaq_hist = nasdaq_ad.history(period=period)

            if nyse_hist.empty and nasdaq_hist.empty:
                logger.warning("No A/D data retrieved")
                return {}

            # Calculate cumulative A/D line
            # Positive change = more advances than declines
            result = {}

            if not nyse_hist.empty:
                nyse_change = nyse_hist['Close'].iloc[-1] - nyse_hist['Close'].iloc[0]
                nyse_pct_change = (nyse_change / nyse_hist['Close'].iloc[0]) * 100
                result['nyse_ad_change'] = float(nyse_change)
                result['nyse_ad_pct'] = float(nyse_pct_change)

            if not nasdaq_hist.empty:
                nasdaq_change = nasdaq_hist['Close'].iloc[-1] - nasdaq_hist['Close'].iloc[0]
                nasdaq_pct_change = (nasdaq_change / nasdaq_hist['Close'].iloc[0]) * 100
                result['nasdaq_ad_change'] = float(nasdaq_change)
                result['nasdaq_ad_pct'] = float(nasdaq_pct_change)

            # Determine overall sentiment
            avg_pct = (result.get('nyse_ad_pct', 0) + result.get('nasdaq_ad_pct', 0)) / 2

            if avg_pct > 5:
                sentiment = "bullish"
                score = 0.6
                description = "Strong market breadth - many stocks advancing"
            elif avg_pct > 0:
                sentiment = "slightly_bullish"
                score = 0.2
                description = "Positive market breadth"
            elif avg_pct > -5:
                sentiment = "slightly_bearish"
                score = -0.2
                description = "Negative market breadth"
            else:
                sentiment = "bearish"
                score = -0.6
                description = "Weak market breadth - many stocks declining"

            result.update({
                'sentiment': sentiment,
                'score': score,
                'description': description,
                'avg_pct_change': avg_pct,
                'timestamp': datetime.now()
            })

            return result

        except Exception as e:
            logger.error(f"Error fetching A/D line data: {e}")
            return {}

    # ==================== Put/Call Ratio ====================

    def get_put_call_ratio_estimate(self, ticker: str = "SPY") -> Dict:
        """
        Estimate put/call ratio using options volume data.

        Put/Call Ratio interpretation:
        - Ratio > 1.0: More puts than calls (bearish sentiment)
        - Ratio = 1.0: Equal puts and calls (neutral)
        - Ratio < 1.0: More calls than puts (bullish sentiment)
        - Ratio > 1.5: Extreme bearishness (contrarian bullish signal)

        Args:
            ticker: Stock or ETF ticker (SPY for S&P 500)

        Returns:
            Dictionary with put/call analysis

        Source: Yahoo Finance options data (FREE)
        Note: CBOE official P/C ratio requires paid data or scraping
        """
        try:
            logger.info(f"Estimating put/call ratio for {ticker}")

            # Get options data from yfinance
            stock = yf.Ticker(ticker)

            # Get available expiration dates
            expirations = stock.options

            if not expirations:
                logger.warning(f"No options data available for {ticker}")
                return {}

            # Use nearest expiration date
            nearest_exp = expirations[0]

            # Get options chain
            options = stock.option_chain(nearest_exp)

            # Calculate total volume for puts and calls
            calls_volume = options.calls['volume'].sum()
            puts_volume = options.puts['volume'].sum()

            # Calculate put/call ratio
            if calls_volume > 0:
                pc_ratio = puts_volume / calls_volume
            else:
                pc_ratio = 0

            # Determine sentiment
            if pc_ratio > 1.5:
                sentiment = "extreme_bearish"
                score = 0.3  # Contrarian bullish signal
                description = "Extreme bearishness (contrarian buy signal)"
            elif pc_ratio > 1.0:
                sentiment = "bearish"
                score = -0.4
                description = "More puts than calls - bearish sentiment"
            elif pc_ratio > 0.7:
                sentiment = "neutral"
                score = 0.0
                description = "Balanced put/call ratio"
            else:
                sentiment = "bullish"
                score = 0.4
                description = "More calls than puts - bullish sentiment"

            return {
                'ticker': ticker,
                'put_call_ratio': float(pc_ratio),
                'puts_volume': int(puts_volume),
                'calls_volume': int(calls_volume),
                'expiration': nearest_exp,
                'sentiment': sentiment,
                'score': score,
                'description': description,
                'timestamp': datetime.now()
            }

        except Exception as e:
            logger.error(f"Error calculating put/call ratio: {e}")
            return {}

    # ==================== Fear & Greed Index ====================

    def get_fear_greed_index_alternative(self) -> Dict:
        """
        Get Fear & Greed Index from Alternative.me (Crypto focused).

        For stock market Fear & Greed, CNN's index would be ideal but
        requires web scraping. This crypto index can serve as a proxy
        for overall market sentiment.

        Returns:
            Dictionary with fear/greed data

        Source: Alternative.me API (FREE, no key needed)
        """
        try:
            logger.info("Fetching Fear & Greed Index")

            # Alternative.me provides a free API for crypto fear & greed
            url = "https://api.alternative.me/fng/"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()

            data = response.json()

            if 'data' not in data or not data['data']:
                return {}

            latest = data['data'][0]

            value = int(latest['value'])
            classification = latest['value_classification']

            # Convert to sentiment score
            # 0-25: Extreme Fear (-0.8)
            # 25-45: Fear (-0.4)
            # 45-55: Neutral (0.0)
            # 55-75: Greed (0.4)
            # 75-100: Extreme Greed (0.8)

            if value < 25:
                score = -0.8
            elif value < 45:
                score = -0.4
            elif value < 55:
                score = 0.0
            elif value < 75:
                score = 0.4
            else:
                score = 0.8

            return {
                'value': value,
                'classification': classification,
                'score': score,
                'timestamp': datetime.fromtimestamp(int(latest['timestamp'])),
                'source': 'Alternative.me (Crypto)'
            }

        except Exception as e:
            logger.error(f"Error fetching Fear & Greed Index: {e}")
            return {}

    # ==================== Market Breadth (S&P 500) ====================

    def get_market_breadth_spy(self, period: str = "1mo") -> Dict:
        """
        Analyze market breadth using SPY vs individual stocks.

        This compares SPY (S&P 500 ETF) performance with typical
        constituent behavior to gauge market health.

        Args:
            period: Time period to analyze

        Returns:
            Dictionary with market breadth analysis
        """
        try:
            logger.info("Analyzing market breadth via SPY")

            # Get SPY data
            spy = yf.Ticker("SPY")
            spy_hist = spy.history(period=period)

            if spy_hist.empty:
                return {}

            # Calculate SPY performance
            spy_return = ((spy_hist['Close'].iloc[-1] / spy_hist['Close'].iloc[0]) - 1) * 100
            spy_volatility = spy_hist['Close'].pct_change().std() * 100

            # Simple breadth indicator: if SPY is up but VIX is also up, it's narrow leadership
            vix_data = self.get_vix(period=period)

            if vix_data:
                # If market is up but VIX is high: narrow breadth (bad)
                # If market is up and VIX is low: broad breadth (good)
                if spy_return > 0 and vix_data['current_vix'] > 20:
                    sentiment = "narrow_leadership"
                    score = 0.1
                    description = "Market up but volatility high - narrow breadth"
                elif spy_return > 0:
                    sentiment = "broad_strength"
                    score = 0.6
                    description = "Market up with low volatility - healthy breadth"
                elif spy_return < -5:
                    sentiment = "broad_weakness"
                    score = -0.6
                    description = "Broad market weakness"
                else:
                    sentiment = "neutral"
                    score = 0.0
                    description = "Mixed market breadth"
            else:
                sentiment = "unknown"
                score = 0.0
                description = "Unable to assess breadth"

            return {
                'spy_return_pct': float(spy_return),
                'spy_volatility': float(spy_volatility),
                'sentiment': sentiment,
                'score': score,
                'description': description,
                'timestamp': datetime.now()
            }

        except Exception as e:
            logger.error(f"Error analyzing market breadth: {e}")
            return {}

    # ==================== Composite Sentiment Score ====================

    def get_overall_market_sentiment(self) -> Dict:
        """
        Calculate composite market sentiment from all indicators.

        Combines:
        - VIX (volatility/fear)
        - Advance/Decline (breadth)
        - Put/Call Ratio (options sentiment)
        - Market Breadth (SPY analysis)

        Returns:
            Dictionary with composite sentiment analysis
        """
        try:
            logger.info("Calculating overall market sentiment")

            # Collect all indicators
            vix = self.get_vix()
            ad_line = self.get_advance_decline_line()
            pc_ratio = self.get_put_call_ratio_estimate("SPY")
            breadth = self.get_market_breadth_spy()

            # Calculate weighted average score
            scores = []
            weights = []

            if vix:
                scores.append(vix['score'])
                weights.append(0.3)  # VIX gets 30% weight

            if ad_line:
                scores.append(ad_line['score'])
                weights.append(0.3)  # A/D gets 30% weight

            if pc_ratio:
                scores.append(pc_ratio['score'])
                weights.append(0.2)  # P/C gets 20% weight

            if breadth:
                scores.append(breadth['score'])
                weights.append(0.2)  # Breadth gets 20% weight

            if not scores:
                logger.warning("No indicator data available")
                return {}

            # Calculate weighted average
            composite_score = sum(s * w for s, w in zip(scores, weights)) / sum(weights)

            # Classify sentiment
            if composite_score > 0.4:
                sentiment = "bullish"
            elif composite_score > 0.1:
                sentiment = "slightly_bullish"
            elif composite_score > -0.1:
                sentiment = "neutral"
            elif composite_score > -0.4:
                sentiment = "slightly_bearish"
            else:
                sentiment = "bearish"

            return {
                'composite_score': composite_score,
                'sentiment': sentiment,
                'vix': vix,
                'advance_decline': ad_line,
                'put_call_ratio': pc_ratio,
                'market_breadth': breadth,
                'timestamp': datetime.now()
            }

        except Exception as e:
            logger.error(f"Error calculating overall sentiment: {e}")
            return {}


# Example usage and testing
if __name__ == "__main__":
    """
    Test the market indicators collector.
    All indicators are FREE - no API keys needed!
    """
    print("\n" + "="*70)
    print("MARKET SENTIMENT INDICATORS - FREE DATA SOURCES")
    print("="*70 + "\n")

    collector = MarketIndicators()

    # Test 1: VIX
    print("1. VIX (Volatility Index)")
    print("-" * 70)
    vix = collector.get_vix(period="1mo")
    if vix:
        print(f"Current VIX: {vix['current_vix']:.2f}")
        print(f"Average VIX (1mo): {vix['avg_vix']:.2f}")
        print(f"Sentiment: {vix['sentiment']}")
        print(f"Description: {vix['description']}")
        print(f"Score: {vix['score']:.2f}")
    else:
        print("❌ VIX data unavailable")

    print("\n2. Advance/Decline Line")
    print("-" * 70)
    ad = collector.get_advance_decline_line(period="1mo")
    if ad:
        print(f"NYSE A/D Change: {ad.get('nyse_ad_pct', 0):.2f}%")
        print(f"NASDAQ A/D Change: {ad.get('nasdaq_ad_pct', 0):.2f}%")
        print(f"Sentiment: {ad['sentiment']}")
        print(f"Description: {ad['description']}")
        print(f"Score: {ad['score']:.2f}")
    else:
        print("❌ A/D data unavailable")

    print("\n3. Put/Call Ratio (SPY)")
    print("-" * 70)
    pc = collector.get_put_call_ratio_estimate("SPY")
    if pc:
        print(f"Put/Call Ratio: {pc['put_call_ratio']:.2f}")
        print(f"Puts Volume: {pc['puts_volume']:,}")
        print(f"Calls Volume: {pc['calls_volume']:,}")
        print(f"Sentiment: {pc['sentiment']}")
        print(f"Description: {pc['description']}")
        print(f"Score: {pc['score']:.2f}")
    else:
        print("❌ P/C ratio unavailable")

    print("\n4. Market Breadth (SPY)")
    print("-" * 70)
    breadth = collector.get_market_breadth_spy(period="1mo")
    if breadth:
        print(f"SPY Return: {breadth['spy_return_pct']:.2f}%")
        print(f"SPY Volatility: {breadth['spy_volatility']:.2f}%")
        print(f"Sentiment: {breadth['sentiment']}")
        print(f"Description: {breadth['description']}")
        print(f"Score: {breadth['score']:.2f}")
    else:
        print("❌ Breadth data unavailable")

    print("\n" + "="*70)
    print("OVERALL MARKET SENTIMENT")
    print("="*70)

    overall = collector.get_overall_market_sentiment()
    if overall:
        print(f"\nComposite Score: {overall['composite_score']:.2f}")
        print(f"Overall Sentiment: {overall['sentiment'].upper()}")
        print(f"\nTimestamp: {overall['timestamp']}")
    else:
        print("\n❌ Unable to calculate overall sentiment")

    print("\n" + "="*70)
    print("All data sources are FREE - no API keys required!")
    print("Data provided by Yahoo Finance via yfinance library")
    print("="*70 + "\n")
