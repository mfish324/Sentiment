# Twitter API Issues & Solutions

## The Problem: Error 400

If you're getting an **Error 400** from Twitter API, this is because Twitter changed their API access in 2023-2024.

### What Happened?

**Before (2023)**:
- Free tier included tweet search
- 500,000 tweets/month limit
- Perfect for projects like this

**Now (2024-2025)**:
- Free tier is **extremely limited** (write-only)
- Search requires **Basic tier**: **$100/month**
- Or **Pro tier**: **$5,000/month**

### Twitter API Tiers (Current)

| Tier | Cost | Search Access | Notes |
|------|------|---------------|-------|
| **Free** | $0 | ❌ No | Write-only (post tweets) |
| **Basic** | $100/month | ✅ Yes | 10,000 tweets/month |
| **Pro** | $5,000/month | ✅ Yes | 1M tweets/month |

## Solutions

### Solution 1: Use FMP Instead (Recommended)

The app now includes Financial Modeling Prep (FMP) API which provides:
- Institutional holdings data
- Insider trading data
- **FREE** tier (250 requests/day)
- More reliable than social media sentiment

**Setup**: See [FMP_SETUP_GUIDE.md](FMP_SETUP_GUIDE.md)

**Run without Twitter**:
```bash
python src/main.py --ticker AAPL --no-twitter
```

### Solution 2: Pay for Twitter Basic ($100/month)

If you really need Twitter data:

1. Go to: https://developer.twitter.com/en/portal/products/basic
2. Subscribe to Basic tier ($100/month)
3. Your existing API keys will work
4. Remove `--no-twitter` flag

### Solution 3: Use Alternative Social Media

Consider these free alternatives (would need new modules):

**Reddit API** (Free):
- r/wallstreetbets
- r/stocks
- r/investing
- Much better for stock sentiment than Twitter anyway!

**StockTwits API** (Free tier available):
- Stock-focused social network
- Better signal-to-noise for stocks
- Easier to analyze

## Why FMP is Better Than Twitter Anyway

### Twitter Sentiment Issues:

1. **Sarcasm**: "Great, another market crash! 🙄" = Looks positive to algorithms
2. **Bots**: Lots of fake accounts pumping stocks
3. **Noise**: Most tweets aren't actionable
4. **Retail-focused**: Doesn't show what "smart money" is doing

### FMP/Institutional Data Benefits:

1. **Real Actions**: Actual buy/sell transactions
2. **Smart Money**: See what Vanguard, BlackRock do
3. **Insider Info**: Executives know their company best
4. **Verified**: All SEC-filed data
5. **Free**: 250 API calls/day

## Institutional Data > Social Media?

Research shows:

| Signal | Predictive Power | Cost |
|--------|-----------------|------|
| Institutional buying | ⭐⭐⭐⭐⭐ | Free (FMP) |
| Insider buying | ⭐⭐⭐⭐ | Free (FMP/SEC) |
| Twitter sentiment | ⭐⭐ | $100/month |
| Reddit sentiment | ⭐⭐⭐ | Free |

## Recommended Approach

**Best Setup for Beginners (All Free)**:

```env
# config/.env

# Skip Twitter - too expensive
# TWITTER_BEARER_TOKEN=skip

# Use FMP - Free and better data
FMP_API_KEY=your_free_fmp_key

# Use SEC - Free official data
SEC_USER_AGENT=Your Name your@email.com
```

**Run Analysis**:
```bash
python src/main.py --ticker AAPL --no-twitter
```

You get:
- ✅ SEC Form 4 (insider trading)
- ✅ FMP institutional holdings
- ✅ FMP insider trades
- ✅ Sentiment analysis
- ✅ All FREE

## If You Still Want Twitter

### Error 400: Bad Request

**Possible Causes:**

1. **No search access** (free tier)
   - Solution: Upgrade to Basic ($100/month)

2. **Invalid bearer token**
   - Solution: Regenerate in Twitter Developer Portal

3. **Expired credentials**
   - Solution: Generate new tokens

4. **Query format issue**
   - Check: Are you searching correctly? ($AAPL format)

### Error 403: Forbidden

- Your app doesn't have permission
- Check app permissions in Developer Portal
- Make sure you have "Read" permission enabled

### Error 429: Rate Limit

- You hit the rate limit
- Wait 15 minutes
- The app should handle this automatically

### Error 401: Unauthorized

- Invalid API credentials
- Check config/.env for typos
- Regenerate your bearer token

## Testing Your Twitter Setup

If you have Twitter Basic tier, test with:

```bash
# Activate venv
Sent\Scripts\activate

# Test Twitter collector
python src/data_sources/twitter_collector.py
```

If it works, you'll see tweets!

## Future: Add Reddit Support

If there's interest, we can add Reddit API support:

**Pros**:
- Free API
- Stock-focused subreddits
- Better signal than Twitter
- More detailed discussions

**Implementation**: Would add `reddit_collector.py` similar to Twitter module

## Summary

**The Reality**:
- Twitter API is now expensive ($100/month)
- For most users, institutional data (FMP) is better anyway
- FMP is free and shows what "smart money" is doing

**Recommendation**:
1. ✅ Use FMP (free, better data)
2. ✅ Use SEC EDGAR (free, official)
3. ❌ Skip Twitter (unless you pay $100/month)
4. 🤔 Consider adding Reddit later (free)

---

**Bottom Line**: The Error 400 isn't a bug - it's Twitter's business model now. Use FMP instead!
