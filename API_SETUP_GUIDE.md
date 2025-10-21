# API Setup Guide

Detailed instructions for obtaining API credentials for each data source.

## Twitter/X API Setup

### Step 1: Create a Twitter Developer Account

1. Go to [Twitter Developer Portal](https://developer.twitter.com/en/portal/dashboard)
2. Sign in with your Twitter account
3. Click **"Sign up for Free Account"** (if you don't have developer access yet)
4. Fill out the application form:
   - **What's your use case?** Select "Exploring the API"
   - **Will you make Twitter content available to a government entity?** No
   - Describe your project briefly (e.g., "Building a stock market sentiment analysis tool for educational purposes")
5. Agree to terms and submit

**Note:** Approval is usually instant for basic access, but can take a few hours.

### Step 2: Create a New App

1. Once approved, go to the [Developer Portal Dashboard](https://developer.twitter.com/en/portal/dashboard)
2. Click **"Create Project"**
   - Project name: "Stock Sentiment Analyzer" (or any name)
   - Use case: "Exploring the API"
   - Project description: Brief description of your app
3. Click **"Create App"** within your project
   - App name: "sentiment-analyzer" (must be unique globally)
   - Click "Complete"

### Step 3: Get Your API Keys

1. After creating the app, you'll see your **API Key** and **API Secret Key**
   - **IMPORTANT:** Save these immediately! They won't be shown again.
   - Copy them to a secure location

2. Generate Access Tokens:
   - In your app dashboard, go to the **"Keys and tokens"** tab
   - Under "Authentication Tokens", click **"Generate"** for Access Token and Secret
   - Save these tokens

3. Get Bearer Token (Required for API v2):
   - In the same "Keys and tokens" tab
   - You'll see the **Bearer Token**
   - Click "Generate" if it's not already created
   - Save this token

### Step 4: Set App Permissions (Optional)

By default, your app has "Read" permissions, which is all we need.

If you want to verify:
1. Go to **"Settings"** tab
2. Scroll to **"App permissions"**
3. Ensure it's set to **"Read"**

### Step 5: Add Keys to Your .env File

Open `config/.env` and add your keys:

```env
TWITTER_API_KEY=your_api_key_here
TWITTER_API_SECRET=your_api_secret_here
TWITTER_ACCESS_TOKEN=your_access_token_here
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret_here
TWITTER_BEARER_TOKEN=your_bearer_token_here
```

**Example (with fake keys):**
```env
TWITTER_API_KEY=abc123xyz789ABC123XYZ789
TWITTER_API_SECRET=def456uvw012DEF456UVW012def456uvw012DEF456UVW
TWITTER_ACCESS_TOKEN=123456789-ghi789rst345GHI789RST345
TWITTER_ACCESS_TOKEN_SECRET=jkl012mno678JKL012MNO678jkl012mno678JK
TWITTER_BEARER_TOKEN=AAAAAAAAAAAAAAAAAAAAAA%2FAAAAAAAAAA%3DAAAAAAA
```

### Twitter API Limits (Free Tier)

| Endpoint | Rate Limit |
|----------|------------|
| Search Recent Tweets | 450 requests per 15 minutes |
| Tweet Lookup | 300 requests per 15 minutes |
| Monthly Tweet Cap | 500,000 tweets |

**What this means:**
- You can make about 30 requests per minute
- Each request can fetch up to 100 tweets
- The app automatically handles rate limiting

### Testing Your Twitter Setup

Run this to test your credentials:

```bash
python src/data_sources/twitter_collector.py
```

If successful, you'll see sample tweets about Apple stock!

---

## SEC EDGAR Setup

### Good News: No API Key Required!

The SEC EDGAR database is completely free and doesn't require API keys.

### Only Requirement: User Agent Header

The SEC requires you to identify yourself in requests.

#### Step 1: Add Your Email to .env

Open `config/.env` and update this line:

```env
SEC_USER_AGENT=Your Name your.email@example.com
```

**Example:**
```env
SEC_USER_AGENT=John Smith john.smith@gmail.com
```

**Important:**
- Use your real name and email
- The SEC uses this to contact you if there are issues with your requests
- This is a requirement, not optional

#### Step 2: Respect Rate Limits

- **Maximum:** 10 requests per second
- The app automatically enforces this limit
- Don't try to bypass it - the SEC monitors this

### SEC Data Available

| Filing Type | Description | Update Frequency |
|-------------|-------------|------------------|
| Form 4 | Insider trading | Real-time (within 2 business days) |
| 13F | Institutional holdings | Quarterly (45 days after quarter end) |
| 8-K | Major events | As they occur |
| 10-Q | Quarterly report | Quarterly |
| 10-K | Annual report | Annually |

### Testing Your SEC Setup

Run this to test:

```bash
python src/data_sources/sec_edgar_collector.py
```

If successful, you'll see insider trading filings for Apple!

---

## Future Data Sources (Not Yet Implemented)

### Reddit API

**Status:** Not included in initial version (can be added later)

To add Reddit data:
1. Go to [Reddit Apps](https://www.reddit.com/prefs/apps)
2. Create a new app
3. Get your Client ID and Secret
4. Use PRAW (Python Reddit API Wrapper)

### Alpha Vantage (Stock Prices)

**Status:** Not included in initial version (can be added later)

To add stock price data:
1. Go to [Alpha Vantage](https://www.alphavantage.co/support/#api-key)
2. Get a free API key (500 requests/day)
3. Use their API to fetch stock prices and fundamentals

### Yahoo Finance

**Status:** Not included in initial version (can be added later)

Alternative to Alpha Vantage:
- No API key required
- Use `yfinance` Python library
- Unlimited free access (unofficial API)

---

## Troubleshooting

### Twitter Issues

**Error: "Unauthorized"**
- Double-check your API keys in `.env`
- Make sure there are no extra spaces or quotes
- Regenerate your keys if needed

**Error: "Rate limit exceeded"**
- The app should handle this automatically
- If it doesn't, reduce the number of tweets you're requesting

**Error: "Could not authenticate you"**
- Your Bearer Token might be incorrect
- Regenerate it in the Twitter Developer Portal

### SEC Issues

**Error: "HTTP 403 Forbidden"**
- Check your User-Agent in `.env`
- Make sure it contains a valid email
- Don't use "example.com" - use a real email

**Error: "Too many requests"**
- You're exceeding 10 requests/second
- The app should prevent this, but if it happens, add delays

---

## Security Best Practices

### Protect Your API Keys

1. **Never commit `.env` to version control**
   - The `.gitignore` file already excludes it
   - Double-check before pushing to GitHub

2. **Regenerate keys if exposed**
   - If you accidentally share your keys, regenerate them immediately
   - Go to Twitter Developer Portal → Keys and Tokens → Regenerate

3. **Use environment variables**
   - Don't hardcode keys in your Python files
   - Always use the `Config` class to access them

4. **Limit app permissions**
   - Only request "Read" access for Twitter
   - Don't request more permissions than you need

---

## Getting Help

### Twitter API Support
- [Twitter API Documentation](https://developer.twitter.com/en/docs/twitter-api)
- [Tweepy Documentation](https://docs.tweepy.org/)
- [Twitter Developer Community](https://twittercommunity.com/)

### SEC EDGAR Support
- [SEC EDGAR Guide](https://www.sec.gov/edgar/searchedgar/accessing-edgar-data.htm)
- [SEC Developer Resources](https://www.sec.gov/developer)

---

**Ready to start?** Go back to [QUICKSTART.md](QUICKSTART.md) or [README.md](README.md)
