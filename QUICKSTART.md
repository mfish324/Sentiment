# Quick Start Guide

Get up and running in 5 minutes!

## 1. Install Python Packages

```bash
# Activate virtual environment (if you're using one)
# Windows:
venv\Scripts\activate
# Mac/Linux:
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## 2. Run Setup Script

```bash
python setup.py
```

This will:
- Create your `.env` file
- Set up directories
- Download required NLTK data

## 3. Add Your API Keys

Edit `config/.env` and add your credentials:

### Twitter API Keys
1. Go to: https://developer.twitter.com/en/portal/dashboard
2. Create a new app
3. Copy your keys to `.env`

### SEC User Agent
Just add your email:
```
SEC_USER_AGENT=Your Name your.email@example.com
```

## 4. Run Your First Analysis

```bash
python src/main.py --ticker AAPL --tweets 50
```

This analyzes Apple stock using 50 tweets.

## Example Output

```
📱 TWITTER SENTIMENT
----------------------------------------------------------------------
  Total Tweets Analyzed: 50
  Average Sentiment: 0.234
  Positive: 45.0%
  Negative: 15.0%
  Neutral: 40.0%

📄 SEC FILINGS (INSIDER ACTIVITY)
----------------------------------------------------------------------
  Recent Form 4 Filings: 5
  Activity Level: 5 insider transaction(s) in recent period

📊 OVERALL SENTIMENT
----------------------------------------------------------------------
  Sentiment Score: 0.234
  Classification: Positive
```

## More Examples

```bash
# Analyze Tesla
python src/main.py --ticker TSLA --tweets 100

# Analyze multiple stocks
python src/main.py --ticker AAPL MSFT GOOGL --tweets 50

# Create visualizations (after collecting data)
python src/visualization/sentiment_visualizer.py
```

## Troubleshooting

### "Unauthorized" error
- Check your Twitter API keys in `config/.env`
- Make sure there are no extra spaces

### "No module named X"
- Run: `pip install -r requirements.txt`
- Make sure your virtual environment is activated

### No tweets found
- Try a more popular stock (AAPL, TSLA, MSFT)
- The free Twitter API only searches last 7 days

## What's Next?

- Read the full [README.md](README.md) for detailed documentation
- Test individual modules to understand how they work
- Create visualizations of your data
- Extend the app with new data sources!

## Quick Reference

| Command | Description |
|---------|-------------|
| `python src/main.py --ticker AAPL --tweets 100` | Analyze Apple with 100 tweets |
| `python src/visualization/sentiment_visualizer.py` | Create charts |
| `python src/analysis/sentiment_analyzer.py` | Test sentiment analyzer |
| `python setup.py` | Run setup again |

---

**Need Help?** Check [README.md](README.md) for detailed instructions and troubleshooting.
