"""
Sentiment Analysis Module
This module analyzes text sentiment using multiple methods and provides
a unified sentiment score on a scale from -1 (very negative) to +1 (very positive).
"""

from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import logging
from typing import Dict, List
import re

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """
    Analyzes sentiment of text using multiple algorithms.

    This class combines two popular sentiment analysis libraries:
    - TextBlob: General-purpose sentiment analysis
    - VADER: Specialized for social media text (handles slang, emojis, etc.)

    The final score is a weighted average of both methods.
    """

    def __init__(self):
        """Initialize the sentiment analyzer with both TextBlob and VADER."""
        # VADER is particularly good for social media text
        self.vader = SentimentIntensityAnalyzer()
        logger.info("Sentiment analyzer initialized")

    def clean_text(self, text: str) -> str:
        """
        Clean and preprocess text before analysis.

        Args:
            text: Raw text to clean

        Returns:
            Cleaned text

        This removes URLs, extra whitespace, and other noise.
        """
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)

        # Remove @mentions and #hashtags (but keep the text after #)
        text = re.sub(r'@\w+', '', text)
        text = re.sub(r'#', '', text)

        # Remove extra whitespace
        text = ' '.join(text.split())

        return text.strip()

    def analyze_with_textblob(self, text: str) -> Dict[str, float]:
        """
        Analyze sentiment using TextBlob.

        Args:
            text: Text to analyze

        Returns:
            Dictionary with polarity (-1 to 1) and subjectivity (0 to 1)

        Polarity: -1 = very negative, 0 = neutral, 1 = very positive
        Subjectivity: 0 = very objective, 1 = very subjective/opinionated
        """
        try:
            blob = TextBlob(text)
            return {
                'polarity': blob.sentiment.polarity,
                'subjectivity': blob.sentiment.subjectivity
            }
        except Exception as e:
            logger.error(f"TextBlob analysis error: {e}")
            return {'polarity': 0.0, 'subjectivity': 0.0}

    def analyze_with_vader(self, text: str) -> Dict[str, float]:
        """
        Analyze sentiment using VADER (Valence Aware Dictionary and sEntiment Reasoner).

        Args:
            text: Text to analyze

        Returns:
            Dictionary with sentiment scores

        VADER is specifically designed for social media text and handles:
        - Emojis and emoticons
        - Slang
        - Capitalization for emphasis
        - Punctuation (!!!)

        Returns scores for:
        - positive: positive sentiment strength (0 to 1)
        - negative: negative sentiment strength (0 to 1)
        - neutral: neutral sentiment strength (0 to 1)
        - compound: overall sentiment (-1 to 1)
        """
        try:
            scores = self.vader.polarity_scores(text)
            return scores
        except Exception as e:
            logger.error(f"VADER analysis error: {e}")
            return {'compound': 0.0, 'positive': 0.0, 'negative': 0.0, 'neutral': 1.0}

    def analyze(self, text: str) -> Dict[str, float]:
        """
        Perform comprehensive sentiment analysis.

        Args:
            text: Text to analyze

        Returns:
            Dictionary containing:
            - sentiment_score: Combined score from -1 (negative) to 1 (positive)
            - textblob_score: TextBlob polarity score
            - vader_score: VADER compound score
            - confidence: Confidence in the analysis (0 to 1)
            - subjectivity: How subjective/opinionated the text is (0 to 1)

        The final sentiment_score is a weighted average:
        - VADER gets 60% weight (better for social media)
        - TextBlob gets 40% weight (good for general text)
        """
        # Clean the text first
        cleaned_text = self.clean_text(text)

        if not cleaned_text:
            logger.warning("Empty text after cleaning")
            return {
                'sentiment_score': 0.0,
                'textblob_score': 0.0,
                'vader_score': 0.0,
                'confidence': 0.0,
                'subjectivity': 0.0
            }

        # Get scores from both analyzers
        textblob_result = self.analyze_with_textblob(cleaned_text)
        vader_result = self.analyze_with_vader(cleaned_text)

        # Calculate weighted average (VADER gets more weight for social media)
        vader_weight = 0.6
        textblob_weight = 0.4

        combined_score = (
            vader_result['compound'] * vader_weight +
            textblob_result['polarity'] * textblob_weight
        )

        # Calculate confidence based on agreement between methods
        # If both methods agree (both positive or both negative), confidence is higher
        agreement = 1 - abs(vader_result['compound'] - textblob_result['polarity']) / 2
        confidence = agreement

        return {
            'sentiment_score': combined_score,
            'textblob_score': textblob_result['polarity'],
            'vader_score': vader_result['compound'],
            'confidence': confidence,
            'subjectivity': textblob_result['subjectivity'],
            'vader_positive': vader_result['positive'],
            'vader_negative': vader_result['negative'],
            'vader_neutral': vader_result['neutral']
        }

    def analyze_batch(self, texts: List[str]) -> List[Dict[str, float]]:
        """
        Analyze sentiment for multiple texts.

        Args:
            texts: List of text strings to analyze

        Returns:
            List of sentiment analysis results

        Example:
            tweets = ["Great stock!", "Market crash!", "Neutral news"]
            results = analyzer.analyze_batch(tweets)
        """
        return [self.analyze(text) for text in texts]

    def get_overall_sentiment(self, texts: List[str]) -> Dict[str, float]:
        """
        Calculate overall sentiment across multiple texts.

        Args:
            texts: List of text strings

        Returns:
            Dictionary with aggregated sentiment metrics

        This is useful for understanding the overall sentiment about a topic
        across many tweets or posts.
        """
        if not texts:
            return {
                'average_sentiment': 0.0,
                'positive_count': 0,
                'negative_count': 0,
                'neutral_count': 0,
                'total_count': 0
            }

        # Analyze all texts
        results = self.analyze_batch(texts)

        # Calculate statistics
        total = len(results)
        average_sentiment = sum(r['sentiment_score'] for r in results) / total

        # Count positive, negative, and neutral
        # Using thresholds: > 0.05 = positive, < -0.05 = negative, else neutral
        positive_threshold = 0.05
        negative_threshold = -0.05

        positive_count = sum(1 for r in results if r['sentiment_score'] > positive_threshold)
        negative_count = sum(1 for r in results if r['sentiment_score'] < negative_threshold)
        neutral_count = total - positive_count - negative_count

        return {
            'average_sentiment': average_sentiment,
            'positive_count': positive_count,
            'negative_count': negative_count,
            'neutral_count': neutral_count,
            'total_count': total,
            'positive_percentage': (positive_count / total) * 100,
            'negative_percentage': (negative_count / total) * 100,
            'neutral_percentage': (neutral_count / total) * 100
        }

    def classify_sentiment(self, score: float) -> str:
        """
        Convert numerical sentiment score to a text label.

        Args:
            score: Sentiment score from -1 to 1

        Returns:
            String label: "Very Positive", "Positive", "Neutral", "Negative", or "Very Negative"
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


# Example usage and testing
if __name__ == "__main__":
    """
    Test the sentiment analyzer with example texts.
    """
    print("\n=== Testing Sentiment Analyzer ===\n")

    # Create analyzer instance
    analyzer = SentimentAnalyzer()

    # Test examples
    test_texts = [
        "This stock is going to the moon! 🚀🚀🚀 Best investment ever!",
        "Terrible earnings report. Selling all my shares.",
        "The company released their quarterly report today.",
        "I'm a bit worried about the market crash, but staying optimistic!",
        "HODL!!! Don't panic sell! 💎🙌"
    ]

    print("Individual Analysis:")
    print("-" * 80)
    for text in test_texts:
        result = analyzer.analyze(text)
        classification = analyzer.classify_sentiment(result['sentiment_score'])

        print(f"\nText: {text}")
        print(f"Sentiment Score: {result['sentiment_score']:.3f}")
        print(f"Classification: {classification}")
        print(f"Confidence: {result['confidence']:.3f}")
        print(f"Subjectivity: {result['subjectivity']:.3f}")

    # Test overall sentiment
    print("\n" + "=" * 80)
    print("Overall Sentiment Analysis:")
    print("-" * 80)
    overall = analyzer.get_overall_sentiment(test_texts)
    print(f"Average Sentiment: {overall['average_sentiment']:.3f}")
    print(f"Positive: {overall['positive_count']} ({overall['positive_percentage']:.1f}%)")
    print(f"Neutral: {overall['neutral_count']} ({overall['neutral_percentage']:.1f}%)")
    print(f"Negative: {overall['negative_count']} ({overall['negative_percentage']:.1f}%)")
