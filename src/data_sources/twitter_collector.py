"""
Twitter/X Data Collector Module
This module handles fetching tweets related to stock market discussions
and performs sentiment analysis on them.
"""

import tweepy
import time
from datetime import datetime, timedelta
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


class TwitterCollector:
    """
    Collects tweets about stocks and performs sentiment analysis.

    This class handles:
    - Authentication with Twitter API
    - Searching for stock-related tweets
    - Rate limiting to avoid hitting API limits
    - Basic data cleaning and formatting
    """

    def __init__(self):
        """
        Initialize the Twitter collector with API credentials.
        Sets up the Tweepy client for API v2.
        """
        try:
            # Create a Twitter API client using Bearer Token (API v2)
            # This is the simplest authentication method for read-only access
            self.client = tweepy.Client(
                bearer_token=Config.TWITTER_BEARER_TOKEN,
                wait_on_rate_limit=True  # Automatically wait if we hit rate limits
            )
            logger.info("Twitter API client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Twitter client: {e}")
            raise

    def search_tweets(
        self,
        query: str,
        max_results: int = 100,
        start_time: Optional[datetime] = None
    ) -> List[Dict]:
        """
        Search for tweets matching a query.

        Args:
            query: Search query (e.g., "$AAPL" for Apple stock, "stock market crash")
            max_results: Maximum number of tweets to retrieve (10-100 per request)
            start_time: Only get tweets after this time (default: last 24 hours)

        Returns:
            List of dictionaries containing tweet data

        Example:
            tweets = collector.search_tweets("$AAPL", max_results=50)
        """
        # If no start time provided, default to last 24 hours
        if start_time is None:
            start_time = datetime.utcnow() - timedelta(hours=24)

        try:
            logger.info(f"Searching for tweets with query: {query}")

            # Use Twitter API v2 to search recent tweets
            # tweet_fields: Additional data to retrieve about each tweet
            response = self.client.search_recent_tweets(
                query=query,
                max_results=min(max_results, 100),  # API limit is 100 per request
                start_time=start_time,
                tweet_fields=['created_at', 'public_metrics', 'author_id', 'lang'],
                # public_metrics includes: retweet_count, reply_count, like_count, quote_count
            )

            # Process the response
            tweets = []
            if response.data:
                for tweet in response.data:
                    # Convert tweet object to a dictionary with relevant fields
                    tweet_data = {
                        'id': tweet.id,
                        'text': tweet.text,
                        'created_at': tweet.created_at,
                        'author_id': tweet.author_id,
                        'language': tweet.lang,
                        'retweet_count': tweet.public_metrics['retweet_count'],
                        'like_count': tweet.public_metrics['like_count'],
                        'reply_count': tweet.public_metrics['reply_count'],
                        'quote_count': tweet.public_metrics['quote_count'],
                    }
                    tweets.append(tweet_data)

                logger.info(f"Retrieved {len(tweets)} tweets")
            else:
                logger.warning("No tweets found for the query")

            return tweets

        except tweepy.TweepyException as e:
            logger.error(f"Twitter API error: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error while searching tweets: {e}")
            return []

    def search_stock_tweets(
        self,
        ticker: str,
        max_results: int = 100,
        include_cashtag: bool = True
    ) -> List[Dict]:
        """
        Search for tweets about a specific stock ticker.

        Args:
            ticker: Stock ticker symbol (e.g., "AAPL", "TSLA")
            max_results: Maximum number of tweets to retrieve
            include_cashtag: If True, searches for $TICKER format

        Returns:
            List of tweet dictionaries

        Example:
            apple_tweets = collector.search_stock_tweets("AAPL")
        """
        # Format the query with cashtag ($) if requested
        if include_cashtag:
            query = f"${ticker.upper()}"
        else:
            query = ticker.upper()

        # Add filters to get only English tweets and exclude retweets for cleaner data
        # -is:retweet means "exclude retweets"
        # lang:en means "only English tweets"
        query += " -is:retweet lang:en"

        return self.search_tweets(query, max_results=max_results)

    def search_multiple_tickers(
        self,
        tickers: List[str],
        max_results_per_ticker: int = 50
    ) -> Dict[str, List[Dict]]:
        """
        Search for tweets about multiple stock tickers.

        Args:
            tickers: List of stock ticker symbols
            max_results_per_ticker: Max tweets to retrieve per ticker

        Returns:
            Dictionary mapping ticker to list of tweets

        Example:
            results = collector.search_multiple_tickers(["AAPL", "TSLA", "MSFT"])
            apple_tweets = results["AAPL"]
        """
        all_tweets = {}

        for ticker in tickers:
            logger.info(f"Fetching tweets for {ticker}")
            tweets = self.search_stock_tweets(ticker, max_results=max_results_per_ticker)
            all_tweets[ticker] = tweets

            # Be nice to the API - add a small delay between requests
            time.sleep(1)

        return all_tweets

    def get_trending_topics(self, max_results: int = 100) -> List[Dict]:
        """
        Get tweets about general stock market trends and sentiment.

        Args:
            max_results: Maximum number of tweets to retrieve

        Returns:
            List of tweet dictionaries

        Example:
            trending = collector.get_trending_topics()
        """
        # Search for general market-related keywords
        queries = [
            "stock market",
            "stocks",
            "trading",
            "investing"
        ]

        # Combine queries with OR operator
        combined_query = " OR ".join([f'"{q}"' for q in queries])
        combined_query += " -is:retweet lang:en"

        return self.search_tweets(combined_query, max_results=max_results)


# Example usage (for testing)
if __name__ == "__main__":
    """
    This section runs only when you execute this file directly.
    It's useful for testing the module.
    """
    # Create a collector instance
    collector = TwitterCollector()

    # Test: Search for tweets about Apple stock
    print("\n=== Testing Twitter Collector ===")
    print("Searching for $AAPL tweets...")

    tweets = collector.search_stock_tweets("AAPL", max_results=10)

    print(f"\nFound {len(tweets)} tweets:")
    for i, tweet in enumerate(tweets[:3], 1):  # Show first 3 tweets
        print(f"\n--- Tweet {i} ---")
        print(f"Text: {tweet['text'][:100]}...")  # First 100 characters
        print(f"Created: {tweet['created_at']}")
        print(f"Likes: {tweet['like_count']}, Retweets: {tweet['retweet_count']}")
