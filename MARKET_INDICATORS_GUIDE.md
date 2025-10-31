# Market Sentiment Indicators Guide

## Overview

This module provides **FREE** broad market sentiment indicators to complement your stock-specific analysis. These indicators help you understand the overall market environment when evaluating individual stocks.

## Why Market Indicators Matter

**Individual Stock Analysis** tells you about ONE stock.
**Market Indicators** tell you about the ENTIRE market environment.

### Example:
- **Your stock analysis says**: "AAPL sentiment is bullish"
- **Market indicators say**: "Overall market is in panic mode (VIX > 35)"
- **Better decision**: Maybe wait for market to stabilize before buying

## Available Indicators (All FREE!)

### 1. VIX - Volatility Index

**What it is**: The "fear gauge" - measures expected market volatility

**Interpretation**:
- **VIX < 15**: Low fear, complacent market (⚠️ Could mean complacency)
- **VIX 15-25**: Normal conditions (✅ Healthy market)
- **VIX 25-35**: Elevated fear (⚠️ Uncertainty)
- **VIX > 35**: Extreme fear/panic (💥 Crisis mode - but contrarian opportunity!)

**Source**: Yahoo Finance via yfinance (FREE)
**Ticker**: `^VIX`

### 2. Put/Call Ratio

**What it is**: Ratio of put options (bearish bets) to call options (bullish bets)

**Interpretation**:
- **Ratio < 0.7**: More calls than puts = Bullish sentiment
- **Ratio 0.7-1.0**: Balanced = Neutral
- **Ratio 1.0-1.5**: More puts = Bearish sentiment
- **Ratio > 1.5**: Extreme bearishness = **Contrarian BUY signal!**

**Why > 1.5 is bullish**: When everyone is extremely bearish, market often bounces

**Source**: Yahoo Finance options data (FREE)
**Calculated from**: SPY options volume

### 3. Market Breadth

**What it is**: Measures how broadly the market is moving

**Interpretation**:
- **SPY up + Low VIX**: Broad strength (✅ Many stocks rising)
- **SPY up + High VIX**: Narrow leadership (⚠️ Only a few stocks rising)
- **SPY down**: Broad weakness (❌ Most stocks falling)

**Why it matters**: A market rally with broad participation is healthier than one driven by just a few stocks

**Source**: SPY performance + VIX analysis (FREE)

### 4. Advance/Decline Line (A/D Line)

**What it is**: Tracks how many stocks are advancing vs declining each day

**Interpretation**:
- **A/D line rising**: Many stocks advancing = Healthy market
- **A/D line falling**: Many stocks declining = Weak market
- **Divergence**: Market index up but A/D down = Warning sign!

**Source**: NYSE/NASDAQ advance-decline data (FREE)
**Note**: Yahoo Finance A/D tickers changed recently, may need updates

### 5. Composite Market Sentiment

**What it is**: Weighted average of all indicators

**Calculation**:
- VIX: 30% weight
- Advance/Decline: 30% weight
- Put/Call Ratio: 20% weight
- Market Breadth: 20% weight

**Interpretation**:
- **Score > 0.4**: Bullish market environment
- **Score 0.1 to 0.4**: Slightly bullish
- **Score -0.1 to 0.1**: Neutral
- **Score -0.4 to -0.1**: Slightly bearish
- **Score < -0.4**: Bearish market environment

## How to Use

### Quick Test

```bash
# Activate your venv
Sent\Scripts\activate

# Run the market indicators test
python src/data_sources/market_indicators.py
```

You'll see:
```
VIX: 16.90 (neutral)
Put/Call Ratio: 1.34 (bearish)
Market Breadth: SPY +2.78% (broad_strength)
Overall Sentiment: NEUTRAL (score: 0.06)
```

### Using in Your Code

```python
from src.data_sources.market_indicators import MarketIndicators

# Create collector
collector = MarketIndicators()

# Get overall market sentiment
sentiment = collector.get_overall_market_sentiment()

print(f"Market sentiment: {sentiment['sentiment']}")
print(f"Composite score: {sentiment['composite_score']:.2f}")

# Individual indicators
vix = collector.get_vix()
print(f"VIX: {vix['current_vix']:.2f} - {vix['description']}")

pc_ratio = collector.get_put_call_ratio_estimate("SPY")
print(f"Put/Call Ratio: {pc_ratio['put_call_ratio']:.2f}")
```

## Integration with Stock Analysis

### Example Workflow:

1. **Check Market Environment**:
   ```python
   market = collector.get_overall_market_sentiment()
   if market['composite_score'] < -0.5:
       print("⚠️ Market in bearish mode - be cautious!")
   ```

2. **Analyze Your Stock**:
   ```bash
   python src/main.py --ticker AAPL --no-twitter
   ```

3. **Make Decision**:
   - **Stock bullish + Market bullish** = Strong buy signal
   - **Stock bullish + Market bearish** = Wait or smaller position
   - **Stock bearish + Market bearish** = Strong avoid signal
   - **Stock bearish + Market bullish** = Stock-specific issue

## Real-World Examples

### Example 1: False Positive

**Scenario**:
- Your analysis shows: "AAPL has bullish Twitter sentiment"
- Market indicators show: VIX = 38, Put/Call = 1.8, Market Sentiment = bearish

**Interpretation**: Even if AAPL looks good, the entire market is in panic mode. Individual stocks rarely rise when market is crashing.

**Decision**: Wait for market to stabilize

### Example 2: Contrarian Opportunity

**Scenario**:
- Market indicators show: VIX = 40, Put/Call = 1.6 (extreme fear)
- Your analysis shows: Institutional buying increasing

**Interpretation**: Everyone is panicking (contrarian buy signal) + smart money is buying

**Decision**: Potentially a good buying opportunity if you have conviction

### Example 3: Divergence Warning

**Scenario**:
- S&P 500 hitting new highs
- But A/D line declining (fewer stocks participating)
- VIX rising despite market gains

**Interpretation**: Rally is getting narrow - only a few stocks holding market up

**Decision**: Be cautious, potential market top forming

## Indicator Cheat Sheet

| Indicator | Bullish Signal | Bearish Signal | Extreme/Contrarian |
|-----------|----------------|----------------|-------------------|
| **VIX** | < 15 (calm) | 25-35 (fear) | > 35 (panic = buy opportunity) |
| **Put/Call** | < 0.7 | 1.0-1.5 | > 1.5 (extreme fear = bullish!) |
| **A/D Line** | Rising | Falling | Divergence from index |
| **Breadth** | Market up + Low VIX | Market down | Market up + High VIX |

## Advanced: Contrarian Signals

**When Fear is Extreme, It's Often Time to Buy**:

- **VIX > 35 + Put/Call > 1.5** = Maximum fear = Contrarian buy
- **VIX < 12 + Put/Call < 0.6** = Maximum greed = Be cautious

**Why?** Markets are cyclical. When everyone is fearful, bad news is already priced in. When everyone is greedy, any bad news causes crash.

## Data Sources (All FREE!)

| Indicator | Source | Cost | Update Frequency |
|-----------|--------|------|------------------|
| VIX | Yahoo Finance | FREE | Real-time (15min delay) |
| Put/Call Ratio | Yahoo Finance Options | FREE | Daily |
| Market Breadth | SPY + VIX analysis | FREE | Daily |
| A/D Line | NYSE/NASDAQ data | FREE | Daily |

## Limitations

1. **VIX is S&P 500 specific**: Doesn't cover small-caps
2. **Put/Call estimated**: Uses SPY options, not official CBOE data
3. **15-minute delay**: Yahoo Finance data is slightly delayed
4. **A/D tickers**: May need updates as Yahoo changes symbols

## Comparison: Free vs Paid

### What You Get FREE (This Module):
- ✅ VIX data
- ✅ Put/Call ratio estimate
- ✅ Market breadth analysis
- ✅ Composite sentiment score
- ✅ No API keys needed
- ✅ Unlimited requests

### What Paid Services Offer:
- Official CBOE Put/Call ratio (vs estimated)
- Real-time data (vs 15-min delay)
- More granular breadth metrics
- Additional indicators (McClellan Oscillator, etc.)

**For most users**: The free version is sufficient!

## Troubleshooting

### "No VIX data retrieved"
- **Solution**: Check internet connection, Yahoo Finance might be down
- **Alternative**: Try again in a few minutes

### "No A/D data retrieved"
- **Solution**: Yahoo Finance changed A/D ticker symbols
- **Workaround**: A/D calculation is less critical, use other indicators

### "No options data for SPY"
- **Solution**: Options data updates daily after market close
- **Workaround**: Use previous day's data or skip Put/Call ratio

## Next Steps

### Integrate with Your Analysis:

```bash
# Check market conditions before analyzing stocks
python src/data_sources/market_indicators.py

# If market looks good, analyze your stock
python src/main.py --ticker AAPL --no-twitter
```

### Future Enhancements:

We could add:
- **McClellan Oscillator** (advanced breadth indicator)
- **New Highs/New Lows** (another breadth measure)
- **Sector Rotation** (which sectors are leading)
- **Fear & Greed Index** (CNN's composite indicator)

---

## Summary

✅ **What You Have**:
- VIX (fear gauge) - Working
- Put/Call Ratio - Working
- Market Breadth - Working
- Composite Sentiment - Working

✅ **All FREE** - No API keys, no rate limits

✅ **Use Case**: Check market environment before trading individual stocks

**Remember**: Don't fight the market! Even the best stock can fall in a bear market, and even a weak stock can rise in a bull market.

---

**Ready to test?**
```bash
python src/data_sources/market_indicators.py
```
