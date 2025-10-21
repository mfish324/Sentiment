"""
Database Manager Module
Handles all database operations for storing sentiment data.

Uses SQLite - a simple, file-based database that doesn't require a server.
Perfect for beginners and small-to-medium projects.
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional, Any
import logging
from pathlib import Path

# Import our configuration
import sys
sys.path.append(str(Path(__file__).parent.parent.parent))
from config.config import Config

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Manages database operations for the sentiment analysis app.

    This class handles:
    - Creating database tables
    - Storing tweets and sentiment scores
    - Storing SEC filing data
    - Querying historical data
    """

    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize the database manager.

        Args:
            db_path: Path to the SQLite database file (uses config default if not provided)
        """
        self.db_path = db_path or Config.DATABASE_PATH

        # Ensure the database directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Create tables if they don't exist
        self.create_tables()

        logger.info(f"Database initialized at: {self.db_path}")

    def get_connection(self) -> sqlite3.Connection:
        """
        Get a database connection.

        Returns:
            SQLite connection object

        Note: SQLite connections should be created per-thread.
        """
        conn = sqlite3.connect(self.db_path)
        # This makes rows behave like dictionaries
        conn.row_factory = sqlite3.Row
        return conn

    def create_tables(self):
        """
        Create all necessary database tables.

        Tables created:
        - tweets: Stores tweet data and sentiment scores
        - sec_filings: Stores SEC filing information
        - sentiment_summary: Aggregated sentiment scores by ticker and date
        """
        conn = self.get_connection()
        cursor = conn.cursor()

        # Table 1: Twitter/Social Media Data
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tweets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tweet_id TEXT UNIQUE NOT NULL,
                ticker TEXT NOT NULL,
                text TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL,
                author_id TEXT,
                language TEXT,
                retweet_count INTEGER DEFAULT 0,
                like_count INTEGER DEFAULT 0,
                reply_count INTEGER DEFAULT 0,
                quote_count INTEGER DEFAULT 0,
                sentiment_score REAL,
                textblob_score REAL,
                vader_score REAL,
                confidence REAL,
                subjectivity REAL,
                collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(tweet_id)
            )
        ''')

        # Table 2: SEC EDGAR Filings
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sec_filings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                cik TEXT NOT NULL,
                filing_type TEXT NOT NULL,
                filing_date DATE NOT NULL,
                description TEXT,
                document_link TEXT,
                collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(ticker, filing_type, filing_date)
            )
        ''')

        # Table 3: Daily Sentiment Summary
        # This aggregates sentiment by ticker and date for easier querying
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sentiment_summary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                date DATE NOT NULL,
                source TEXT NOT NULL,
                average_sentiment REAL,
                positive_count INTEGER DEFAULT 0,
                negative_count INTEGER DEFAULT 0,
                neutral_count INTEGER DEFAULT 0,
                total_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(ticker, date, source)
            )
        ''')

        # Create indexes for faster queries
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_tweets_ticker ON tweets(ticker)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_tweets_created ON tweets(created_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_filings_ticker ON sec_filings(ticker)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_filings_date ON sec_filings(filing_date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_summary_ticker_date ON sentiment_summary(ticker, date)')

        conn.commit()
        conn.close()

        logger.info("Database tables created/verified")

    def insert_tweet(self, tweet_data: Dict, sentiment_data: Dict) -> bool:
        """
        Insert a tweet with its sentiment analysis into the database.

        Args:
            tweet_data: Dictionary with tweet information (from Twitter API)
            sentiment_data: Dictionary with sentiment scores (from SentimentAnalyzer)

        Returns:
            True if successful, False otherwise
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                INSERT OR IGNORE INTO tweets (
                    tweet_id, ticker, text, created_at, author_id, language,
                    retweet_count, like_count, reply_count, quote_count,
                    sentiment_score, textblob_score, vader_score, confidence, subjectivity
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                str(tweet_data['id']),
                tweet_data.get('ticker', ''),
                tweet_data['text'],
                tweet_data['created_at'],
                tweet_data.get('author_id', ''),
                tweet_data.get('language', ''),
                tweet_data.get('retweet_count', 0),
                tweet_data.get('like_count', 0),
                tweet_data.get('reply_count', 0),
                tweet_data.get('quote_count', 0),
                sentiment_data['sentiment_score'],
                sentiment_data['textblob_score'],
                sentiment_data['vader_score'],
                sentiment_data['confidence'],
                sentiment_data['subjectivity']
            ))

            conn.commit()
            conn.close()
            return True

        except sqlite3.IntegrityError:
            # Tweet already exists
            logger.debug(f"Tweet {tweet_data['id']} already in database")
            return False
        except Exception as e:
            logger.error(f"Error inserting tweet: {e}")
            return False

    def insert_tweets_batch(self, tweets_with_sentiment: List[tuple]) -> int:
        """
        Insert multiple tweets at once (more efficient).

        Args:
            tweets_with_sentiment: List of tuples (tweet_data, sentiment_data)

        Returns:
            Number of tweets successfully inserted
        """
        inserted_count = 0
        for tweet_data, sentiment_data in tweets_with_sentiment:
            if self.insert_tweet(tweet_data, sentiment_data):
                inserted_count += 1
        return inserted_count

    def insert_sec_filing(self, filing_data: Dict) -> bool:
        """
        Insert an SEC filing into the database.

        Args:
            filing_data: Dictionary with filing information

        Returns:
            True if successful, False otherwise
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                INSERT OR IGNORE INTO sec_filings (
                    ticker, cik, filing_type, filing_date, description, document_link
                ) VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                filing_data['ticker'],
                filing_data['cik'],
                filing_data['filing_type'],
                filing_data['filing_date'],
                filing_data.get('description', ''),
                filing_data.get('document_link', '')
            ))

            conn.commit()
            conn.close()
            return True

        except sqlite3.IntegrityError:
            logger.debug(f"Filing already exists: {filing_data['ticker']} {filing_data['filing_type']} {filing_data['filing_date']}")
            return False
        except Exception as e:
            logger.error(f"Error inserting SEC filing: {e}")
            return False

    def get_tweet_sentiment(self, ticker: str, days: int = 7) -> List[Dict]:
        """
        Get recent tweet sentiment for a ticker.

        Args:
            ticker: Stock ticker symbol
            days: Number of days of history to retrieve

        Returns:
            List of tweet records with sentiment
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT * FROM tweets
                WHERE ticker = ?
                AND created_at >= datetime('now', '-' || ? || ' days')
                ORDER BY created_at DESC
            ''', (ticker, days))

            rows = cursor.fetchall()
            conn.close()

            # Convert to list of dictionaries
            return [dict(row) for row in rows]

        except Exception as e:
            logger.error(f"Error querying tweets: {e}")
            return []

    def get_sentiment_summary(self, ticker: str, days: int = 30) -> Dict:
        """
        Get aggregated sentiment summary for a ticker.

        Args:
            ticker: Stock ticker symbol
            days: Number of days to aggregate

        Returns:
            Dictionary with sentiment statistics
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT
                    COUNT(*) as total_tweets,
                    AVG(sentiment_score) as avg_sentiment,
                    SUM(CASE WHEN sentiment_score > 0.05 THEN 1 ELSE 0 END) as positive_count,
                    SUM(CASE WHEN sentiment_score < -0.05 THEN 1 ELSE 0 END) as negative_count,
                    SUM(CASE WHEN sentiment_score BETWEEN -0.05 AND 0.05 THEN 1 ELSE 0 END) as neutral_count,
                    AVG(confidence) as avg_confidence
                FROM tweets
                WHERE ticker = ?
                AND created_at >= datetime('now', '-' || ? || ' days')
            ''', (ticker, days))

            row = cursor.fetchone()
            conn.close()

            if row:
                result = dict(row)
                total = result['total_tweets'] or 1  # Avoid division by zero
                result['positive_percentage'] = (result['positive_count'] / total) * 100
                result['negative_percentage'] = (result['negative_count'] / total) * 100
                result['neutral_percentage'] = (result['neutral_count'] / total) * 100
                return result
            else:
                return {}

        except Exception as e:
            logger.error(f"Error getting sentiment summary: {e}")
            return {}

    def get_sec_filings(self, ticker: str, filing_type: Optional[str] = None) -> List[Dict]:
        """
        Get SEC filings for a ticker.

        Args:
            ticker: Stock ticker symbol
            filing_type: Optional filter by filing type (e.g., "4", "13F-HR")

        Returns:
            List of filing records
        """
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            if filing_type:
                cursor.execute('''
                    SELECT * FROM sec_filings
                    WHERE ticker = ? AND filing_type = ?
                    ORDER BY filing_date DESC
                ''', (ticker, filing_type))
            else:
                cursor.execute('''
                    SELECT * FROM sec_filings
                    WHERE ticker = ?
                    ORDER BY filing_date DESC
                ''', (ticker,))

            rows = cursor.fetchall()
            conn.close()

            return [dict(row) for row in rows]

        except Exception as e:
            logger.error(f"Error querying SEC filings: {e}")
            return []


# Example usage and testing
if __name__ == "__main__":
    """
    Test the database manager.
    """
    print("\n=== Testing Database Manager ===\n")

    # Create database instance
    db = DatabaseManager()

    # Test 1: Insert a sample tweet
    print("Test 1: Inserting sample tweet")
    print("-" * 60)

    sample_tweet = {
        'id': '1234567890',
        'ticker': 'AAPL',
        'text': 'Apple stock looking great! 🚀',
        'created_at': datetime.now(),
        'author_id': 'user123',
        'language': 'en',
        'retweet_count': 10,
        'like_count': 50,
        'reply_count': 5,
        'quote_count': 2
    }

    sample_sentiment = {
        'sentiment_score': 0.75,
        'textblob_score': 0.7,
        'vader_score': 0.8,
        'confidence': 0.85,
        'subjectivity': 0.6
    }

    success = db.insert_tweet(sample_tweet, sample_sentiment)
    print(f"Tweet inserted: {success}\n")

    # Test 2: Query sentiment
    print("Test 2: Querying sentiment for AAPL")
    print("-" * 60)

    summary = db.get_sentiment_summary('AAPL', days=30)
    if summary and summary.get('total_tweets', 0) > 0:
        print(f"Total tweets: {summary['total_tweets']}")
        print(f"Average sentiment: {summary['avg_sentiment']:.3f}")
        print(f"Positive: {summary['positive_percentage']:.1f}%")
        print(f"Negative: {summary['negative_percentage']:.1f}%")
        print(f"Neutral: {summary['neutral_percentage']:.1f}%")
    else:
        print("No tweets found in database")

    print("\nDatabase location:", db.db_path)
