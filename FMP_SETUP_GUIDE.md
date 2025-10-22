# Financial Modeling Prep (FMP) API Setup Guide

## Overview

The Financial Modeling Prep (FMP) API has been added as an alternative/supplement to Twitter and SEC EDGAR for institutional data. FMP provides clean, easy-to-use access to:

- **Institutional Holdings** (13F filings)
- **Mutual Fund Holdings**
- **Insider Trading** transactions
- **Stock Ownership** data

## Why FMP?

1. **Better than Twitter**: Twitter API is now very expensive ($100/month for basic search)
2. **Easier than SEC**: FMP processes SEC filings into clean JSON (no XML parsing needed)
3. **Free Tier Available**: 250 API calls per day
4. **Comprehensive Data**: Combines multiple SEC filing types in one place

## Getting Your API Key

### Step 1: Sign Up

1. Go to: https://site.financialmodelingprep.com/developer/docs
2. Click "Get Your Free API Key"
3. Fill out the registration form
4. Verify your email address

### Step 2: Get Your API Key

1. Log in to your FMP account
2. Go to your dashboard
3. Copy your API key (looks like: `a1b2c3d4e5f6g7h8i9j0`)

### Step 3: Add to Your Config

Open `config/.env` and add:

```env
FMP_API_KEY=your_actual_api_key_here
```

**Example:**
```env
FMP_API_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6
```

## API Limits

### Free Tier
- **250 requests per day**
- All endpoints available
- Real-time data
- Perfect for learning and personal projects

### Paid Tiers (if you need more)
- **Starter**: $14/month - 500 requests/day
- **Professional**: $29/month - 1000 requests/day
- **Enterprise**: Custom pricing

For this sentiment analysis app, the free tier is usually sufficient!

## Testing Your Setup

Once you've added your API key, test it:

```bash
# Activate your venv first (Windows):
Sent\Scripts\activate

# Test the FMP collector
python src/data_sources/fmp_collector.py
```

You should see output like:

```
=== Testing FMP API Collector ===

Test 1: Getting institutional holders for AAPL
------------------------------------------------------------
Found 120 institutional holders:

1. Vanguard Group Inc
   Shares: 1,234,567,890
   Change: 5,000,000
   Date: 2024-03-31

...
```

## Using FMP in Your Analysis

### Option 1: Use FMP Instead of Twitter

Since Twitter API is expensive, you can skip Twitter entirely:

```bash
python src/main.py --ticker AAPL --no-twitter
```

This will use:
- ✅ SEC EDGAR (Form 4 filings)
- ✅ FMP (institutional holdings + insider trades)
- ❌ Twitter (skipped)

### Option 2: Use FMP Standalone

Test just the FMP collector:

```bash
python src/data_sources/fmp_collector.py
```

## Data Available from FMP

### 1. Institutional Holdings (13F Filings)

Shows which big institutions own the stock:

```python
from src.data_sources.fmp_collector import FMPCollector

collector = FMPCollector()
holders = collector.get_institutional_holders("AAPL")

# Shows: Vanguard, BlackRock, State Street, etc.
```

**What it means for sentiment:**
- Increasing institutional ownership = Bullish
- Decreasing institutional ownership = Bearish

### 2. Mutual Fund Holdings

Shows which mutual funds hold the stock:

```python
funds = collector.get_mutual_fund_holders("AAPL")

# Shows: Vanguard Index Funds, Fidelity Funds, etc.
```

### 3. Insider Trading

Shows when executives buy/sell company stock:

```python
trades = collector.get_insider_trades("AAPL")

# Shows: CEO, CFO, Directors buying/selling
```

**What it means for sentiment:**
- Insider buying = Bullish (they know the company best)
- Insider selling = Could be bearish (or just diversification)

### 4. Sentiment Analysis

FMP module includes built-in sentiment analysis:

```python
# Analyze institutional sentiment
inst_sentiment = collector.analyze_institutional_sentiment("AAPL")
print(f"Institutional Sentiment: {inst_sentiment['sentiment']}")
print(f"Score: {inst_sentiment['score']}")

# Analyze insider sentiment
insider_sentiment = collector.analyze_insider_sentiment("AAPL", days=90)
print(f"Insider Sentiment: {insider_sentiment['sentiment']}")
print(f"Buys: {insider_sentiment['buys']}, Sells: {insider_sentiment['sells']}")
```

## Rate Limiting

The FMP collector automatically handles rate limiting:

- Minimum 0.5 seconds between requests
- 250 requests per day limit (free tier)
- Automatic retries on errors

## Comparison: Twitter vs FMP

| Feature | Twitter API | FMP API |
|---------|------------|---------|
| **Cost** | $100/month | Free (250/day) |
| **Data Type** | Social sentiment | Institutional data |
| **Quality** | Noisy, sarcasm issues | Clean, structured |
| **Real-time** | Yes | Yes (daily updates) |
| **Setup** | Complex | Simple |
| **Best For** | Public sentiment | Smart money tracking |

## Troubleshooting

### Error: "FMP API key not configured"

**Solution**: Add your API key to `config/.env`:
```env
FMP_API_KEY=your_key_here
```

### Error: "API limit exceeded"

**Solution**: You've hit the 250 requests/day limit. Wait until tomorrow or upgrade your plan.

### Error: "Invalid API key"

**Solutions**:
1. Check for typos in your API key
2. Make sure there are no extra spaces
3. Regenerate your key on the FMP website
4. Make sure you're using the key from the right account

### No data returned for a ticker

**Solutions**:
- Some small-cap stocks may not have institutional data
- Try a large-cap stock like AAPL, MSFT, TSLA
- Check that the ticker symbol is correct

## Example: Complete Analysis with FMP

```bash
# 1. Activate venv
Sent\Scripts\activate

# 2. Run analysis with FMP data (skip expensive Twitter)
python src/main.py --ticker AAPL --no-twitter

# 3. View results
# You'll see:
# - SEC Form 4 filings (insider trading)
# - FMP institutional holdings
# - FMP insider trade analysis
# - Overall sentiment score
```

## Advanced: Rate Limit Management

If you're analyzing many stocks, manage your API calls:

```python
# Good: Analyze 10 stocks = ~30 API calls (well under 250 limit)
python src/main.py --ticker AAPL MSFT GOOGL AMZN TSLA --no-twitter

# Bad: Don't analyze 100 stocks in one run (will hit limit)
```

Each stock requires about 3-4 FMP API calls:
- 1 call for institutional holders
- 1 call for mutual fund holders
- 1 call for insider trades
- 1 call for ownership data

So 250 calls/day = ~60-80 stocks per day

## Database Storage

FMP data is automatically stored in SQLite:

**Tables:**
- `institutional_holdings` - Who owns the stock
- `fmp_insider_trades` - Insider buy/sell transactions

View your data:
```bash
# Use any SQLite browser or:
sqlite3 data/sentiment.db
sqlite> SELECT * FROM institutional_holdings WHERE ticker='AAPL' LIMIT 5;
```

## Further Documentation

- **FMP API Docs**: https://site.financialmodelingprep.com/developer/docs
- **FMP Pricing**: https://financialmodelingprep.com/developer/docs/pricing
- **FMP Status**: https://status.financialmodelingprep.com/

## Next Steps

1. ✅ Get your free API key
2. ✅ Add it to `config/.env`
3. ✅ Test with `python src/data_sources/fmp_collector.py`
4. ✅ Run analysis: `python src/main.py --ticker AAPL --no-twitter`
5. ✅ Compare institutional vs insider sentiment

---

**Ready to analyze?** Your FMP data will provide institutional-grade insights without the high cost of Twitter API!
