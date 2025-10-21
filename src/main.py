"""
Main Application Entry Point
This is the main file you run to collect and analyze stock market sentiment.

Usage:
    python src/main.py --ticker AAPL --tweets 100
"""

import argparse
import logging
from datetime import datetime
from pathlib import Path
import sys

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

# Import our modules
from config.config import Config
from src.data_sources.twitter_collector import TwitterCollector
from src.data_sources.sec_edgar_collector import SECEdgarCollector
from src.analysis.sentiment_analyzer import SentimentAnalyzer
from src.database.db_manager import DatabaseManager

# Set up logging with colors and formatting
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


class SentimentApp:
    """
    Main application class that coordinates all components.

    This class brings together:
    - Data collection (Twitter, SEC)
    - Sentiment analysis
    - Database storage
    """

    def __init__(self):
        """Initialize all components of the application."""
        logger.info("Initializing Sentiment Analysis App...")

        # Validate configuration
        try:
            Config.validate()
        except ValueError as e:
            logger.error(f"Configuration error: {e}")
            logger.error("Please set up your .env file before running the app")
            sys.exit(1)

        # Initialize components
        self.twitter = TwitterCollector()
        self.sec = SECEdgarCollector()
        self.analyzer = SentimentAnalyzer()
        self.db = DatabaseManager()

        logger.info("All components initialized successfully")

    def collect_twitter_sentiment(self, ticker: str, max_tweets: int = 100):
        """
        Collect and analyze Twitter sentiment for a stock ticker.

        Args:
            ticker: Stock ticker symbol (e.g., "AAPL")
            max_tweets: Maximum number of tweets to collect

        Returns:
            Dictionary with sentiment summary
        """
        logger.info(f"Collecting Twitter sentiment for {ticker}...")

        # Step 1: Collect tweets
        tweets = self.twitter.search_stock_tweets(ticker, max_results=max_tweets)

        if not tweets:
            logger.warning(f"No tweets found for {ticker}")
            return None

        logger.info(f"Collected {len(tweets)} tweets for {ticker}")

        # Step 2: Analyze sentiment for each tweet
        logger.info("Analyzing sentiment...")
        analyzed_count = 0

        for tweet in tweets:
            # Analyze the tweet text
            sentiment = self.analyzer.analyze(tweet['text'])

            # Add ticker to tweet data
            tweet['ticker'] = ticker

            # Store in database
            success = self.db.insert_tweet(tweet, sentiment)
            if success:
                analyzed_count += 1

        logger.info(f"Stored {analyzed_count} new tweets in database")

        # Step 3: Get overall sentiment summary
        summary = self.db.get_sentiment_summary(ticker, days=7)

        return summary

    def collect_sec_data(self, ticker: str):
        """
        Collect SEC filing data for a stock ticker.

        Args:
            ticker: Stock ticker symbol

        Returns:
            Dictionary with filing information
        """
        logger.info(f"Collecting SEC data for {ticker}...")

        # Collect Form 4 (insider trading) filings
        form4_filings = self.sec.get_form4_filings(ticker, count=10)

        # Store filings in database
        stored_count = 0
        for filing in form4_filings:
            success = self.db.insert_sec_filing(filing)
            if success:
                stored_count += 1

        logger.info(f"Stored {stored_count} new SEC filings")

        # Analyze insider sentiment
        insider_sentiment = self.sec.analyze_insider_sentiment(form4_filings)

        return {
            'filing_count': len(form4_filings),
            'insider_sentiment': insider_sentiment,
            'latest_filing': form4_filings[0] if form4_filings else None
        }

    def analyze_stock(self, ticker: str, max_tweets: int = 100):
        """
        Perform complete sentiment analysis for a stock.

        This combines:
        - Twitter sentiment
        - SEC filing data
        - Overall sentiment score

        Args:
            ticker: Stock ticker symbol
            max_tweets: Maximum tweets to collect

        Returns:
            Complete analysis dictionary
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"Starting analysis for {ticker}")
        logger.info(f"{'='*60}\n")

        results = {
            'ticker': ticker,
            'timestamp': datetime.now(),
            'twitter': None,
            'sec': None,
            'overall_sentiment': None
        }

        # Collect Twitter sentiment
        try:
            twitter_sentiment = self.collect_twitter_sentiment(ticker, max_tweets)
            results['twitter'] = twitter_sentiment
        except Exception as e:
            logger.error(f"Error collecting Twitter data: {e}")

        # Collect SEC data
        try:
            sec_data = self.collect_sec_data(ticker)
            results['sec'] = sec_data
        except Exception as e:
            logger.error(f"Error collecting SEC data: {e}")

        # Calculate overall sentiment
        if results['twitter'] and results['twitter'].get('avg_sentiment') is not None:
            results['overall_sentiment'] = {
                'score': results['twitter']['avg_sentiment'],
                'classification': self.analyzer.classify_sentiment(
                    results['twitter']['avg_sentiment']
                )
            }

        return results

    def display_results(self, results: dict):
        """
        Display analysis results in a readable format.

        Args:
            results: Analysis results dictionary
        """
        print("\n" + "="*70)
        print(f"SENTIMENT ANALYSIS REPORT: {results['ticker']}")
        print(f"Generated: {results['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70 + "\n")

        # Twitter Sentiment
        if results['twitter']:
            tw = results['twitter']
            print("📱 TWITTER SENTIMENT")
            print("-" * 70)
            print(f"  Total Tweets Analyzed: {tw.get('total_tweets', 0)}")
            print(f"  Average Sentiment: {tw.get('avg_sentiment', 0):.3f}")
            print(f"  Positive: {tw.get('positive_percentage', 0):.1f}%")
            print(f"  Negative: {tw.get('negative_percentage', 0):.1f}%")
            print(f"  Neutral: {tw.get('neutral_percentage', 0):.1f}%")
            print(f"  Average Confidence: {tw.get('avg_confidence', 0):.3f}")
        else:
            print("📱 TWITTER SENTIMENT: No data available")

        print()

        # SEC Data
        if results['sec']:
            sec = results['sec']
            print("📄 SEC FILINGS (INSIDER ACTIVITY)")
            print("-" * 70)
            print(f"  Recent Form 4 Filings: {sec['filing_count']}")
            if sec['insider_sentiment']:
                ins = sec['insider_sentiment']
                print(f"  Activity Level: {ins['description']}")
                if ins.get('latest_date'):
                    print(f"  Latest Filing: {ins['latest_date']}")
        else:
            print("📄 SEC FILINGS: No data available")

        print()

        # Overall Assessment
        if results['overall_sentiment']:
            overall = results['overall_sentiment']
            print("📊 OVERALL SENTIMENT")
            print("-" * 70)
            print(f"  Sentiment Score: {overall['score']:.3f}")
            print(f"  Classification: {overall['classification']}")
        else:
            print("📊 OVERALL SENTIMENT: Insufficient data")

        print("\n" + "="*70 + "\n")


def main():
    """
    Main function - handles command line arguments and runs the app.
    """
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(
        description='Stock Market Sentiment Analysis Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze Apple stock with 100 tweets
  python src/main.py --ticker AAPL --tweets 100

  # Analyze Tesla with 200 tweets
  python src/main.py --ticker TSLA --tweets 200

  # Analyze multiple stocks
  python src/main.py --ticker AAPL MSFT GOOGL --tweets 50
        """
    )

    parser.add_argument(
        '--ticker',
        nargs='+',
        required=True,
        help='Stock ticker symbol(s) to analyze (e.g., AAPL TSLA MSFT)'
    )

    parser.add_argument(
        '--tweets',
        type=int,
        default=100,
        help='Maximum number of tweets to collect per ticker (default: 100)'
    )

    parser.add_argument(
        '--no-twitter',
        action='store_true',
        help='Skip Twitter data collection'
    )

    parser.add_argument(
        '--no-sec',
        action='store_true',
        help='Skip SEC filing collection'
    )

    args = parser.parse_args()

    # Create app instance
    app = SentimentApp()

    # Analyze each ticker
    for ticker in args.ticker:
        try:
            results = app.analyze_stock(ticker.upper(), max_tweets=args.tweets)
            app.display_results(results)
        except Exception as e:
            logger.error(f"Error analyzing {ticker}: {e}")
            import traceback
            traceback.print_exc()

    logger.info("Analysis complete!")


if __name__ == "__main__":
    main()
