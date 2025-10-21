# Project Structure

Complete overview of the Stock Market Sentiment Analysis App.

## Directory Structure

```
Sentiment/
│
├── config/                          # Configuration files
│   ├── .env.example                # Template for API keys (copy to .env)
│   ├── .env                        # Your actual API keys (DO NOT COMMIT!)
│   ├── config.py                   # Configuration loader
│   └── __init__.py
│
├── src/                            # Source code
│   ├── data_sources/               # Data collection modules
│   │   ├── twitter_collector.py   # Twitter/X API integration
│   │   ├── sec_edgar_collector.py # SEC EDGAR API integration
│   │   └── __init__.py
│   │
│   ├── analysis/                   # Analysis modules
│   │   ├── sentiment_analyzer.py  # Sentiment analysis engine
│   │   └── __init__.py
│   │
│   ├── database/                   # Database operations
│   │   ├── db_manager.py          # SQLite database manager
│   │   └── __init__.py
│   │
│   ├── visualization/              # Visualization tools
│   │   ├── sentiment_visualizer.py # Charts and graphs
│   │   └── __init__.py
│   │
│   ├── main.py                     # Main application entry point
│   └── __init__.py
│
├── data/                           # Data storage (auto-created)
│   └── sentiment.db               # SQLite database
│
├── logs/                           # Application logs (auto-created)
│   └── app.log
│
├── requirements.txt                # Python dependencies
├── setup.py                        # Setup script
├── .gitignore                      # Git ignore rules
│
├── README.md                       # Main documentation
├── QUICKSTART.md                   # Quick start guide
├── API_SETUP_GUIDE.md             # Detailed API setup instructions
└── PROJECT_STRUCTURE.md           # This file
```

## File Descriptions

### Configuration Files

| File | Purpose | Notes |
|------|---------|-------|
| `config/.env.example` | Template for environment variables | Copy to `.env` and fill in |
| `config/.env` | Your actual API keys | **Never commit this!** |
| `config/config.py` | Loads and validates configuration | Reads from `.env` file |

### Data Collection Modules

| File | Purpose | Key Features |
|------|---------|--------------|
| `twitter_collector.py` | Collects tweets via Twitter API | - Searches by ticker symbol<br>- Handles rate limiting<br>- Supports multiple queries |
| `sec_edgar_collector.py` | Fetches SEC filings | - Form 4 (insider trading)<br>- 13F (institutional holdings)<br>- Automatic rate limiting (10/sec) |

### Analysis Modules

| File | Purpose | Key Features |
|------|---------|--------------|
| `sentiment_analyzer.py` | Analyzes text sentiment | - Uses TextBlob + VADER<br>- Returns score -1 to +1<br>- Includes confidence level |

### Database

| File | Purpose | Tables |
|------|---------|--------|
| `db_manager.py` | SQLite database operations | - `tweets`: Tweet data + sentiment<br>- `sec_filings`: SEC filing data<br>- `sentiment_summary`: Daily aggregates |

### Visualization

| File | Purpose | Chart Types |
|------|---------|-------------|
| `sentiment_visualizer.py` | Creates charts and graphs | - Pie charts (distribution)<br>- Gauge charts (overall sentiment)<br>- Comparison bars (multiple tickers) |

### Main Application

| File | Purpose | Features |
|------|---------|----------|
| `main.py` | Application entry point | - Command-line interface<br>- Orchestrates all modules<br>- Generates reports |

### Documentation

| File | Audience | Content |
|------|----------|---------|
| `README.md` | Everyone | Complete documentation |
| `QUICKSTART.md` | Beginners | 5-minute setup guide |
| `API_SETUP_GUIDE.md` | API setup | Detailed credential instructions |
| `PROJECT_STRUCTURE.md` | Developers | This file - architecture overview |

### Utility Files

| File | Purpose |
|------|---------|
| `requirements.txt` | Python package dependencies |
| `setup.py` | One-time setup script |
| `.gitignore` | Prevents committing sensitive files |

## Data Flow

```
User Input (Ticker Symbol)
        ↓
    main.py
        ↓
        ├─→ twitter_collector.py ──→ Twitter API
        │           ↓
        │   sentiment_analyzer.py
        │           ↓
        └─→ sec_edgar_collector.py ─→ SEC EDGAR API
                    ↓
              db_manager.py
                    ↓
              SQLite Database
                    ↓
        ┌───────────┴───────────┐
        ↓                       ↓
   Console Report      sentiment_visualizer.py
                              ↓
                         Charts/Graphs
```

## Module Dependencies

### Twitter Module
```python
tweepy          # Twitter API client
requests        # HTTP requests
```

### Sentiment Analysis
```python
textblob        # General sentiment analysis
vaderSentiment  # Social media sentiment
nltk            # Natural language processing
```

### SEC Module
```python
requests        # HTTP requests
beautifulsoup4  # HTML parsing
lxml            # XML/HTML parser
```

### Database
```python
sqlite3         # Built into Python
pandas          # Data manipulation (optional)
```

### Visualization
```python
matplotlib      # Static charts
plotly          # Interactive charts (optional)
```

## Database Schema

### tweets table
```sql
CREATE TABLE tweets (
    id INTEGER PRIMARY KEY,
    tweet_id TEXT UNIQUE,
    ticker TEXT,
    text TEXT,
    created_at TIMESTAMP,
    sentiment_score REAL,
    textblob_score REAL,
    vader_score REAL,
    confidence REAL,
    subjectivity REAL,
    -- engagement metrics
    retweet_count INTEGER,
    like_count INTEGER,
    reply_count INTEGER,
    quote_count INTEGER
);
```

### sec_filings table
```sql
CREATE TABLE sec_filings (
    id INTEGER PRIMARY KEY,
    ticker TEXT,
    cik TEXT,
    filing_type TEXT,
    filing_date DATE,
    description TEXT,
    document_link TEXT,
    collected_at TIMESTAMP
);
```

### sentiment_summary table
```sql
CREATE TABLE sentiment_summary (
    id INTEGER PRIMARY KEY,
    ticker TEXT,
    date DATE,
    source TEXT,
    average_sentiment REAL,
    positive_count INTEGER,
    negative_count INTEGER,
    neutral_count INTEGER,
    total_count INTEGER
);
```

## Key Classes

### TwitterCollector
```python
class TwitterCollector:
    def __init__(self)
    def search_tweets(query, max_results)
    def search_stock_tweets(ticker, max_results)
    def search_multiple_tickers(tickers)
```

### SentimentAnalyzer
```python
class SentimentAnalyzer:
    def __init__(self)
    def analyze(text) → dict
    def analyze_batch(texts) → list
    def get_overall_sentiment(texts) → dict
```

### SECEdgarCollector
```python
class SECEdgarCollector:
    def __init__(self)
    def get_company_cik(ticker) → str
    def get_recent_filings(ticker, filing_type)
    def get_form4_filings(ticker)
    def analyze_insider_sentiment(filings)
```

### DatabaseManager
```python
class DatabaseManager:
    def __init__(db_path)
    def insert_tweet(tweet_data, sentiment_data)
    def get_tweet_sentiment(ticker, days)
    def get_sentiment_summary(ticker, days)
    def insert_sec_filing(filing_data)
```

## Configuration Variables

### Environment Variables (.env)
```
# Twitter API
TWITTER_API_KEY
TWITTER_API_SECRET
TWITTER_ACCESS_TOKEN
TWITTER_ACCESS_TOKEN_SECRET
TWITTER_BEARER_TOKEN
TWITTER_RATE_LIMIT=450

# SEC EDGAR
SEC_USER_AGENT=Name email@example.com
SEC_RATE_LIMIT=10

# Database
DATABASE_PATH=./data/sentiment.db

# Analysis
SENTIMENT_THRESHOLD_POSITIVE=0.05
SENTIMENT_THRESHOLD_NEGATIVE=-0.05
```

## Extending the Project

### Adding a New Data Source

1. Create new file in `src/data_sources/`
2. Implement collector class
3. Add to `main.py` analysis workflow
4. Create database table if needed
5. Update requirements.txt with dependencies

### Adding a New Analysis Method

1. Create new file in `src/analysis/`
2. Implement analyzer class
3. Integrate with sentiment_analyzer.py
4. Update database schema if needed

### Adding a New Visualization

1. Add method to `sentiment_visualizer.py`
2. Query data from database
3. Create chart using matplotlib/plotly
4. Add example to documentation

## Testing Individual Modules

Each module can be tested independently:

```bash
# Test Twitter collector
python src/data_sources/twitter_collector.py

# Test sentiment analyzer
python src/analysis/sentiment_analyzer.py

# Test SEC collector
python src/data_sources/sec_edgar_collector.py

# Test database
python src/database/db_manager.py

# Test visualizer
python src/visualization/sentiment_visualizer.py
```

## Common Workflows

### Collect and Analyze
```bash
python src/main.py --ticker AAPL --tweets 100
```

### Visualize Results
```bash
python src/visualization/sentiment_visualizer.py
```

### Check Database
```bash
sqlite3 data/sentiment.db
sqlite> SELECT COUNT(*) FROM tweets;
sqlite> SELECT ticker, AVG(sentiment_score) FROM tweets GROUP BY ticker;
```

---

For more information, see:
- [README.md](README.md) - Complete documentation
- [QUICKSTART.md](QUICKSTART.md) - Quick start guide
- [API_SETUP_GUIDE.md](API_SETUP_GUIDE.md) - API credentials setup
