"""
Stock Market Agent - FinanceBot for TradePro Securities
Provides stock prices, market summaries, and financial news.
"""

import random
from datetime import datetime

# Agent Configuration
STOCK_CONFIG = {
    "id": "stock",
    "name": "FinanceBot",
    "company": "TradePro Securities",
    "icon": "📈",
    "color": "#4ECDC4",
    "description": """You are FinanceBot, the professional financial assistant for TradePro Securities.

Your personality:
- Professional, precise, and data-driven
- Use formal but approachable language
- Present information in a clear, structured manner
- Be confident but not overly promotional

Your responsibilities:
- Provide current stock prices and daily changes
- Share market summaries and index performance
- Deliver relevant financial news and market updates
- Help users understand market trends

IMPORTANT DISCLAIMER: Always remind users that:
- This information is for educational purposes only
- This is NOT financial advice
- Users should consult a licensed financial advisor before making investment decisions
- Past performance does not guarantee future results"""
}

# Mock Stock Database
STOCKS = {
    "AAPL": {"name": "Apple Inc.", "base_price": 185.50, "sector": "Technology", "pe_ratio": 28.5},
    "GOOGL": {"name": "Alphabet Inc.", "base_price": 142.30, "sector": "Technology", "pe_ratio": 24.2},
    "MSFT": {"name": "Microsoft Corporation", "base_price": 415.20, "sector": "Technology", "pe_ratio": 35.8},
    "TSLA": {"name": "Tesla Inc.", "base_price": 248.75, "sector": "Automotive", "pe_ratio": 62.4},
    "AMZN": {"name": "Amazon.com Inc.", "base_price": 178.25, "sector": "Consumer Cyclical", "pe_ratio": 42.1},
    "NVDA": {"name": "NVIDIA Corporation", "base_price": 495.80, "sector": "Technology", "pe_ratio": 65.3},
    "JPM": {"name": "JPMorgan Chase & Co.", "base_price": 172.40, "sector": "Financial Services", "pe_ratio": 11.2},
    "V": {"name": "Visa Inc.", "base_price": 275.60, "sector": "Financial Services", "pe_ratio": 29.8},
    "META": {"name": "Meta Platforms Inc.", "base_price": 385.90, "sector": "Technology", "pe_ratio": 26.7},
    "BRK.B": {"name": "Berkshire Hathaway Inc.", "base_price": 362.15, "sector": "Financial Services", "pe_ratio": 8.9},
}

# Market indices
INDICES = {
    "S&P 500": {"base_value": 5021.84, "symbol": "^GSPC"},
    "NASDAQ": {"base_value": 15990.66, "symbol": "^IXIC"},
    "DOW Jones": {"base_value": 38654.42, "symbol": "^DJI"},
    "Russell 2000": {"base_value": 2014.75, "symbol": "^RUT"},
}


async def get_stock_price(symbol: str) -> dict:
    """
    Get the current stock price and daily performance for a ticker symbol.
    
    Args:
        symbol: Stock ticker symbol (e.g., AAPL, GOOGL, MSFT, TSLA)
    
    Returns:
        Dictionary containing current price, daily change, and stock information
    """
    symbol = symbol.upper().strip()
    
    if symbol in STOCKS:
        stock = STOCKS[symbol]
        # Simulate realistic price movement (-3% to +3%)
        change_percent = round(random.uniform(-3, 3), 2)
        change_amount = round(stock["base_price"] * (change_percent / 100), 2)
        current_price = round(stock["base_price"] + change_amount, 2)
        
        # Determine market hours
        hour = datetime.now().hour
        is_market_open = 9 <= hour < 16
        
        return {
            "success": True,
            "symbol": symbol,
            "company_name": stock["name"],
            "current_price": f"${current_price:,.2f}",
            "price_change": f"{'+'if change_amount >= 0 else ''}{change_amount:,.2f}",
            "change_percent": f"{'+'if change_percent >= 0 else ''}{change_percent:.2f}%",
            "trend": "📈 Up" if change_amount >= 0 else "📉 Down",
            "sector": stock["sector"],
            "pe_ratio": stock["pe_ratio"],
            "market_cap": f"${random.randint(100, 3000)}B",
            "volume": f"{random.randint(10, 80)}M shares",
            "market_status": "🟢 Market Open" if is_market_open else "🔴 Market Closed",
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S EST"),
            "disclaimer": "Data is simulated for demonstration purposes."
        }
    
    return {
        "success": False,
        "error": f"Symbol '{symbol}' not found in our database",
        "suggestion": "Try one of these popular symbols:",
        "available_symbols": list(STOCKS.keys()),
        "tip": "Make sure to enter a valid NYSE/NASDAQ ticker symbol"
    }


async def get_market_summary() -> dict:
    """
    Get an overview of major market indices and overall market conditions.
    
    Returns:
        Dictionary containing major indices, market status, and sentiment indicators
    """
    # Generate market data
    indices_data = {}
    overall_trend = 0
    
    for name, data in INDICES.items():
        change_percent = round(random.uniform(-1.5, 1.5), 2)
        change_value = round(data["base_value"] * (change_percent / 100), 2)
        current_value = round(data["base_value"] + change_value, 2)
        overall_trend += change_percent
        
        indices_data[name] = {
            "value": f"{current_value:,.2f}",
            "change": f"{'+'if change_percent >= 0 else ''}{change_percent:.2f}%",
            "trend": "📈" if change_percent >= 0 else "📉"
        }
    
    # Determine market sentiment
    avg_trend = overall_trend / len(INDICES)
    if avg_trend > 0.5:
        sentiment = "🟢 Bullish"
        sentiment_desc = "Markets showing positive momentum"
    elif avg_trend < -0.5:
        sentiment = "🔴 Bearish"
        sentiment_desc = "Markets under pressure"
    else:
        sentiment = "🟡 Neutral"
        sentiment_desc = "Markets trading mixed"
    
    hour = datetime.now().hour
    is_market_open = 9 <= hour < 16
    
    return {
        "success": True,
        "market_status": "🟢 Market Open" if is_market_open else "🔴 Market Closed",
        "trading_session": "Regular Hours" if is_market_open else "After Hours",
        "indices": indices_data,
        "market_sentiment": sentiment,
        "sentiment_description": sentiment_desc,
        "vix_level": f"{random.uniform(12, 25):.2f}",
        "trading_volume": random.choice(["Above Average", "Average", "Below Average"]),
        "top_sectors": ["Technology", "Healthcare", "Financial Services"],
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S EST"),
        "disclaimer": "Market data is simulated. Not for trading decisions."
    }


async def get_stock_news(symbol: str = "") -> dict:
    """
    Get the latest financial news, optionally filtered by stock symbol.
    
    Args:
        symbol: Optional stock ticker to filter news (e.g., AAPL, TSLA)
    
    Returns:
        Dictionary containing relevant news articles and market updates
    """
    # General market news
    general_news = [
        {
            "headline": "Tech Sector Rallies on Strong Q4 Earnings Reports",
            "source": "Reuters",
            "time": "2 hours ago",
            "sentiment": "Positive"
        },
        {
            "headline": "Federal Reserve Signals Steady Interest Rates Through Q1",
            "source": "Bloomberg",
            "time": "4 hours ago",
            "sentiment": "Neutral"
        },
        {
            "headline": "AI Chip Demand Continues to Drive Semiconductor Growth",
            "source": "CNBC",
            "time": "5 hours ago",
            "sentiment": "Positive"
        },
        {
            "headline": "Global Markets Show Mixed Signals Amid Economic Data",
            "source": "Wall Street Journal",
            "time": "6 hours ago",
            "sentiment": "Neutral"
        },
        {
            "headline": "Retail Sales Beat Expectations, Consumer Confidence Rises",
            "source": "MarketWatch",
            "time": "8 hours ago",
            "sentiment": "Positive"
        },
    ]
    
    # Symbol-specific news
    symbol_news = {
        "AAPL": [
            {"headline": "Apple Announces Revolutionary AI Features for Next iPhone", "source": "TechCrunch", "time": "1 hour ago", "sentiment": "Positive"},
            {"headline": "Apple Services Revenue Hits All-Time High", "source": "Apple Insider", "time": "3 hours ago", "sentiment": "Positive"},
        ],
        "TSLA": [
            {"headline": "Tesla Expands Supercharger Network to 50,000 Stations Globally", "source": "Electrek", "time": "2 hours ago", "sentiment": "Positive"},
            {"headline": "Tesla Cybertruck Deliveries Accelerate in Q1", "source": "InsideEVs", "time": "5 hours ago", "sentiment": "Positive"},
        ],
        "NVDA": [
            {"headline": "NVIDIA Reports Record Data Center Revenue on AI Demand", "source": "The Verge", "time": "1 hour ago", "sentiment": "Positive"},
            {"headline": "NVIDIA Unveils Next-Generation AI Chips at CES", "source": "Ars Technica", "time": "4 hours ago", "sentiment": "Positive"},
        ],
        "MSFT": [
            {"headline": "Microsoft Azure Growth Accelerates with AI Integration", "source": "ZDNet", "time": "3 hours ago", "sentiment": "Positive"},
            {"headline": "Microsoft Copilot Adoption Surpasses 100 Million Users", "source": "The Verge", "time": "6 hours ago", "sentiment": "Positive"},
        ],
        "GOOGL": [
            {"headline": "Google Cloud Revenue Jumps 25% on Enterprise AI Deals", "source": "Reuters", "time": "2 hours ago", "sentiment": "Positive"},
            {"headline": "Alphabet Announces $70B Stock Buyback Program", "source": "CNBC", "time": "5 hours ago", "sentiment": "Positive"},
        ],
    }
    
    # Build response
    if symbol:
        symbol = symbol.upper().strip()
        if symbol in symbol_news:
            news = symbol_news[symbol] + general_news[:2]
            filter_applied = symbol
        else:
            news = general_news
            filter_applied = f"{symbol} (no specific news, showing general)"
    else:
        news = general_news
        filter_applied = "All Markets"
    
    return {
        "success": True,
        "filter": filter_applied,
        "article_count": len(news),
        "news": news,
        "market_mood": random.choice(["Optimistic", "Cautious", "Mixed"]),
        "trending_topics": ["AI & Machine Learning", "Interest Rates", "Earnings Season"],
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "disclaimer": "News is for informational purposes only. Not financial advice."
    }


# Export tools list for the agent
stock_tools = [get_stock_price, get_market_summary, get_stock_news]
