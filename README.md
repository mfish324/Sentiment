# Stock Market Sentiment Analysis App

A beginner-friendly Python application that aggregates data from multiple sources to gauge overall stock market sentiment.

## Features

- **Twitter/X Sentiment Analysis**: Collect and analyze real-time stock discussions
- **SEC EDGAR Integration**: Track insider trading (Form 4) and institutional holdings (13F)
- **Advanced Sentiment Scoring**: Uses both TextBlob and VADER for accurate social media sentiment analysis
- **SQLite Database**: Simple local storage for historical data
- **Modular Design**: Easy to extend with additional data sources

## Project Structure

```
Sentiment/
├── config/
│   ├── .env.example          # Template for API keys
│   └── config.py             # Configuration management
├── src/
│   ├── data_sources/
│   │   ├── twitter_collector.py    # Twitter API integration
│   │   └── sec_edgar_collector.py  # SEC EDGAR API integration
│   ├── analysis/
│   │   └── sentiment_analyzer.py   # Sentiment analysis engine
│   ├── database/
│   │   └── db_manager.py          # Database operations
│   └── main.py               # Main application entry point
├── data/                     # Database storage (auto-created)
├── logs/                     # Application logs (auto-created)
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

## Prerequisites

- Python 3.8 or higher
- Twitter/X API access (Developer Account)
- Internet connection

## Installation

### Step 1: Clone or Download the Project

```bash
cd Sentiment
```

### Step 2: Create a Virtual Environment (Recommended)

A virtual environment keeps your project dependencies isolated.

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` appear in your terminal prompt.

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install all required packages including:
- `tweepy` - Twitter API client
- `textblob` and `vaderSentiment` - Sentiment analysis
- `requests` and `beautifulsoup4` - Web scraping for SEC data
- `pandas` and `matplotlib` - Data analysis and visualization
- And more...

### Step 4: Download NLTK Data (Required for TextBlob)

Run this one-time setup:

```bash
python -c "import nltk; nltk.download('brown'); nltk.download('punkt')"
```

## Configuration

### Step 1: Set Up API Keys

1. Copy the example environment file:
   ```bash
   copy config\.env.example config\.env
   ```
   (On macOS/Linux use `cp` instead of `copy`)

2. Edit `config/.env` with your API credentials

### Step 2: Get Twitter API Credentials

1. Go to [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard)
2. Sign up for a developer account (it's free)
3. Create a new project and app
4. In your app settings, go to "Keys and tokens"
5. Generate the following:
   - API Key and Secret
   - Access Token and Secret
   - Bearer Token

6. Add these to your `config/.env` file:
   ```
   TWITTER_API_KEY=your_api_key_here
   TWITTER_API_SECRET=your_api_secret_here
   TWITTER_ACCESS_TOKEN=your_access_token_here
   TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret_here
   TWITTER_BEARER_TOKEN=your_bearer_token_here
   ```

**Important Notes:**
- Free tier has rate limits (450 requests per 15 minutes)
- The app automatically handles rate limiting
- Keep your API keys secret! Never commit them to version control

### Step 3: Configure SEC EDGAR User Agent

The SEC requires you to identify yourself when accessing their data:

In `config/.env`, update this line with your information:
```
SEC_USER_AGENT=YourName your.email@example.com
```

Example:
```
SEC_USER_AGENT=John Smith john.smith@gmail.com
```

This is required and must be a real email address. The SEC uses this to contact you if there are issues with your requests.

## Usage

### Basic Usage

Analyze a single stock:

```bash
python src/main.py --ticker AAPL --tweets 100
```

This will:
1. Collect up to 100 recent tweets about Apple ($AAPL)
2. Analyze sentiment of each tweet
3. Fetch recent SEC Form 4 filings (insider trading)
4. Store everything in the database
5. Display a summary report

### Analyze Multiple Stocks

```bash
python src/main.py --ticker AAPL TSLA MSFT --tweets 50
```

### Command Line Options

- `--ticker SYMBOL [SYMBOL ...]` - Stock ticker(s) to analyze (required)
- `--tweets N` - Maximum tweets to collect per ticker (default: 100)
- `--no-twitter` - Skip Twitter data collection
- `--no-sec` - Skip SEC filing collection

### Examples

```bash
# Analyze Tesla with 200 tweets
python src/main.py --ticker TSLA --tweets 200

# Analyze multiple tech stocks
python src/main.py --ticker AAPL GOOGL MSFT AMZN --tweets 75

# Only collect SEC data (no Twitter)
python src/main.py --ticker AAPL --no-twitter
```

## Understanding the Output

The app displays a report with three sections:

### 1. Twitter Sentiment
```
📱 TWITTER SENTIMENT
----------------------------------------------------------------------
  Total Tweets Analyzed: 100
  Average Sentiment: 0.234
  Positive: 45.0%
  Negative: 15.0%
  Neutral: 40.0%
  Average Confidence: 0.821
```

**What it means:**
- **Average Sentiment**: Score from -1 (very negative) to +1 (very positive)
  - `-1.0 to -0.5`: Very Negative
  - `-0.5 to -0.05`: Negative
  - `-0.05 to 0.05`: Neutral
  - `0.05 to 0.5`: Positive
  - `0.5 to 1.0`: Very Positive
- **Percentages**: Distribution of positive/negative/neutral tweets
- **Confidence**: How confident the algorithm is (0 to 1)

### 2. SEC Filings
```
📄 SEC FILINGS (INSIDER ACTIVITY)
----------------------------------------------------------------------
  Recent Form 4 Filings: 5
  Activity Level: 5 insider transaction(s) in recent period
  Latest Filing: 2024-10-15
```

**What it means:**
- **Form 4 Filings**: Number of insider trading reports
- Higher activity might indicate important company developments
- Check the filing dates to see how recent they are

### 3. Overall Sentiment
```
📊 OVERALL SENTIMENT
----------------------------------------------------------------------
  Sentiment Score: 0.234
  Classification: Positive
```

**What it means:**
- Combined sentiment score and simple classification
- Use this as a general indicator, not investment advice!

## Testing Individual Modules

Each module can be tested independently:

### Test Twitter Collector
```bash
python src/data_sources/twitter_collector.py
```

### Test Sentiment Analyzer
```bash
python src/analysis/sentiment_analyzer.py
```

### Test SEC EDGAR Collector
```bash
python src/data_sources/sec_edgar_collector.py
```

### Test Database
```bash
python src/database/db_manager.py
```

## Database

The app uses SQLite, which stores data in a single file: `data/sentiment.db`

### View Database Contents

You can use any SQLite browser like:
- [DB Browser for SQLite](https://sqlitebrowser.org/) (free, cross-platform)
- [SQLite Viewer](https://sqliteviewer.app/) (web-based)

### Database Tables

1. **tweets** - Stores tweet data and sentiment scores
2. **sec_filings** - Stores SEC filing information
3. **sentiment_summary** - Aggregated daily sentiment by ticker

## Troubleshooting

### "No module named 'tweepy'" or similar errors
**Solution**: Make sure you activated your virtual environment and ran `pip install -r requirements.txt`

### "Twitter API error: Unauthorized"
**Solution**: Check that your API keys in `config/.env` are correct

### "SEC request failed"
**Solution**: Make sure you set a valid email in `SEC_USER_AGENT`

### "No tweets found"
**Solution**:
- The stock ticker might not have much Twitter activity
- Try a more popular stock like AAPL, TSLA, or MSFT
- The Twitter free tier only searches last 7 days of tweets

### Rate Limiting
If you see rate limit messages:
- The app automatically waits and retries
- Twitter free tier: 450 requests per 15 minutes
- SEC: Max 10 requests per second (automatically enforced)

## Limitations & Disclaimers

⚠️ **Important Notes:**

1. **Not Financial Advice**: This tool is for educational purposes only. Do not make investment decisions based solely on sentiment analysis.

2. **Data Limitations**:
   - Twitter free tier only searches last 7 days
   - Sentiment analysis is not 100% accurate
   - Sarcasm and context can be misinterpreted

3. **Rate Limits**:
   - Twitter API has strict rate limits on free tier
   - Be mindful of API usage

4. **SEC Data**: The basic implementation tracks filing activity but doesn't parse detailed transaction data (buy vs sell amounts)

## Next Steps & Extensions

Want to expand the project? Here are some ideas:

1. **Add Reddit Integration**: Collect data from r/wallstreetbets, r/stocks
2. **Add Stock Price Data**: Integrate Yahoo Finance API
3. **Create a Web Dashboard**: Use Dash or Streamlit for visualization
4. **Historical Analysis**: Compare sentiment with actual stock performance
5. **Alerts**: Get notified when sentiment changes significantly
6. **More SEC Filings**: Parse 13F, 8-K, 10-Q filings
7. **Machine Learning**: Train a custom model on financial text

## Learning Resources

New to Python? Check out these resources:

- [Python Official Tutorial](https://docs.python.org/3/tutorial/)
- [Tweepy Documentation](https://docs.tweepy.org/)
- [TextBlob Documentation](https://textblob.readthedocs.io/)
- [SEC EDGAR Guide](https://www.sec.gov/edgar/searchedgar/accessing-edgar-data.htm)

## Support

If you encounter issues:

1. Check the logs in the `logs/` directory
2. Verify your API credentials in `config/.env`
3. Make sure all dependencies are installed
4. Try running the individual module tests

## License

This project is for educational purposes. Please respect API terms of service and rate limits.

---

**Happy Analyzing! 📈**
