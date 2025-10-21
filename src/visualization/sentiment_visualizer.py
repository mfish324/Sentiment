"""
Sentiment Visualization Module
Creates charts and graphs to visualize sentiment data.
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
from typing import List, Dict
import logging
from pathlib import Path
import sys

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))
from src.database.db_manager import DatabaseManager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SentimentVisualizer:
    """
    Creates visualizations of sentiment data.

    This class can generate:
    - Sentiment distribution pie charts
    - Sentiment over time line graphs
    - Comparison charts for multiple tickers
    """

    def __init__(self, db_manager: DatabaseManager = None):
        """
        Initialize the visualizer.

        Args:
            db_manager: Database manager instance (creates new one if not provided)
        """
        self.db = db_manager or DatabaseManager()
        # Set a nice style for plots
        plt.style.use('seaborn-v0_8-darkgrid' if 'seaborn-v0_8-darkgrid' in plt.style.available else 'default')

    def plot_sentiment_distribution(self, ticker: str, days: int = 7, save_path: str = None):
        """
        Create a pie chart showing the distribution of positive/negative/neutral sentiment.

        Args:
            ticker: Stock ticker symbol
            days: Number of days of data to include
            save_path: Optional path to save the figure
        """
        # Get sentiment summary from database
        summary = self.db.get_sentiment_summary(ticker, days=days)

        if not summary or summary.get('total_tweets', 0) == 0:
            logger.warning(f"No data available for {ticker}")
            return

        # Create pie chart
        labels = ['Positive', 'Neutral', 'Negative']
        sizes = [
            summary['positive_count'],
            summary['neutral_count'],
            summary['negative_count']
        ]
        colors = ['#2ecc71', '#95a5a6', '#e74c3c']  # Green, Gray, Red
        explode = (0.1, 0, 0)  # Slightly separate the positive slice

        fig, ax = plt.subplots(figsize=(10, 7))
        ax.pie(sizes, explode=explode, labels=labels, colors=colors,
               autopct='%1.1f%%', shadow=True, startangle=90)

        ax.set_title(f'{ticker} Sentiment Distribution\n(Last {days} days, {summary["total_tweets"]} tweets)',
                     fontsize=16, fontweight='bold')

        # Equal aspect ratio ensures that pie is drawn as a circle
        ax.axis('equal')

        # Add summary text
        avg_sentiment = summary.get('avg_sentiment', 0)
        sentiment_label = self._classify_sentiment(avg_sentiment)

        text_str = f'Average Sentiment: {avg_sentiment:.3f}\n'
        text_str += f'Classification: {sentiment_label}\n'
        text_str += f'Confidence: {summary.get("avg_confidence", 0):.3f}'

        plt.figtext(0.5, 0.02, text_str, ha='center', fontsize=10,
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Saved chart to {save_path}")

        plt.show()

    def plot_sentiment_gauge(self, ticker: str, days: int = 7, save_path: str = None):
        """
        Create a gauge/meter visualization of overall sentiment.

        Args:
            ticker: Stock ticker symbol
            days: Number of days of data to include
            save_path: Optional path to save the figure
        """
        summary = self.db.get_sentiment_summary(ticker, days=days)

        if not summary or summary.get('total_tweets', 0) == 0:
            logger.warning(f"No data available for {ticker}")
            return

        sentiment_score = summary.get('avg_sentiment', 0)

        # Create figure
        fig, ax = plt.subplots(figsize=(10, 6))

        # Create the gauge background
        ax.barh([0], [2], left=[-1], height=0.3, color='#e74c3c', alpha=0.3)  # Negative (red)
        ax.barh([0], [0.1], left=[-0.05], height=0.3, color='#95a5a6', alpha=0.3)  # Neutral (gray)
        ax.barh([0], [1], left=[0.05], height=0.3, color='#2ecc71', alpha=0.3)  # Positive (green)

        # Add the sentiment indicator
        color = '#e74c3c' if sentiment_score < -0.05 else '#2ecc71' if sentiment_score > 0.05 else '#95a5a6'
        ax.plot([sentiment_score], [0], 'o', markersize=20, color=color, zorder=5)

        # Formatting
        ax.set_xlim(-1, 1)
        ax.set_ylim(-0.5, 0.5)
        ax.set_yticks([])
        ax.set_xlabel('Sentiment Score', fontsize=12)
        ax.set_title(f'{ticker} Sentiment Gauge\n(Last {days} days, {summary["total_tweets"]} tweets)',
                     fontsize=16, fontweight='bold')

        # Add labels
        ax.text(-0.5, -0.3, 'Negative', ha='center', fontsize=10, color='#e74c3c')
        ax.text(0, -0.3, 'Neutral', ha='center', fontsize=10, color='#95a5a6')
        ax.text(0.5, -0.3, 'Positive', ha='center', fontsize=10, color='#2ecc71')

        # Add score text
        sentiment_label = self._classify_sentiment(sentiment_score)
        ax.text(sentiment_score, 0.25, f'{sentiment_score:.3f}\n{sentiment_label}',
                ha='center', va='bottom', fontsize=12, fontweight='bold')

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Saved chart to {save_path}")

        plt.show()

    def plot_sentiment_comparison(self, tickers: List[str], days: int = 7, save_path: str = None):
        """
        Create a bar chart comparing sentiment across multiple tickers.

        Args:
            tickers: List of stock ticker symbols
            days: Number of days of data to include
            save_path: Optional path to save the figure
        """
        # Collect data for all tickers
        data = []
        for ticker in tickers:
            summary = self.db.get_sentiment_summary(ticker, days=days)
            if summary and summary.get('total_tweets', 0) > 0:
                data.append({
                    'ticker': ticker,
                    'sentiment': summary.get('avg_sentiment', 0),
                    'tweets': summary.get('total_tweets', 0)
                })

        if not data:
            logger.warning("No data available for any ticker")
            return

        # Create bar chart
        fig, ax = plt.subplots(figsize=(12, 6))

        tickers_list = [d['ticker'] for d in data]
        sentiments = [d['sentiment'] for d in data]
        colors = ['#2ecc71' if s > 0.05 else '#e74c3c' if s < -0.05 else '#95a5a6' for s in sentiments]

        bars = ax.bar(tickers_list, sentiments, color=colors, alpha=0.7, edgecolor='black')

        # Add value labels on bars
        for bar, sentiment, d in zip(bars, sentiments, data):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{sentiment:.3f}\n({d["tweets"]} tweets)',
                   ha='center', va='bottom' if height >= 0 else 'top',
                   fontsize=9)

        # Add horizontal line at zero
        ax.axhline(y=0, color='black', linestyle='-', linewidth=0.8)

        # Formatting
        ax.set_ylabel('Average Sentiment Score', fontsize=12)
        ax.set_xlabel('Stock Ticker', fontsize=12)
        ax.set_title(f'Sentiment Comparison\n(Last {days} days)',
                     fontsize=16, fontweight='bold')
        ax.set_ylim(-1, 1)
        ax.grid(axis='y', alpha=0.3)

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Saved chart to {save_path}")

        plt.show()

    def _classify_sentiment(self, score: float) -> str:
        """
        Convert numerical sentiment score to a text label.

        Args:
            score: Sentiment score from -1 to 1

        Returns:
            String label
        """
        if score >= 0.5:
            return "Very Positive"
        elif score >= 0.05:
            return "Positive"
        elif score > -0.05:
            return "Neutral"
        elif score > -0.5:
            return "Negative"
        else:
            return "Very Negative"


# Example usage
if __name__ == "__main__":
    """
    Test the visualizer with sample data.
    """
    print("\n=== Testing Sentiment Visualizer ===\n")

    visualizer = SentimentVisualizer()

    # Check if we have any data in the database
    db = DatabaseManager()

    # Try to visualize data for AAPL
    print("Attempting to create visualizations for AAPL...")
    print("(Make sure you've run the main app first to collect data)")
    print()

    # Create distribution chart
    print("Creating sentiment distribution chart...")
    visualizer.plot_sentiment_distribution('AAPL', days=7)

    # Create gauge chart
    print("Creating sentiment gauge...")
    visualizer.plot_sentiment_gauge('AAPL', days=7)

    # If you have multiple tickers, compare them
    print("Creating comparison chart...")
    visualizer.plot_sentiment_comparison(['AAPL', 'TSLA', 'MSFT'], days=7)

    print("\nNote: If no charts appear, make sure you've collected data first:")
    print("python src/main.py --ticker AAPL --tweets 50")
