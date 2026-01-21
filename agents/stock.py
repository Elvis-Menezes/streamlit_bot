"""
Stock Market Agent - FinanceBot for TradePro Securities
Provides stock prices, market summaries, and financial news.
Powered by Yahoo Finance via MCP Stock Client.
"""

import logging
from datetime import datetime
from typing import Optional

# Configure logging
logger = logging.getLogger(__name__)

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

# MCP Client instance (will be set by app.py)
_mcp_stock_client = None


def set_stock_client(client):
    """Set the MCP Stock Client instance."""
    global _mcp_stock_client
    _mcp_stock_client = client
    logger.info("MCP Stock Client set for stock agent")


def get_stock_client():
    """Get the MCP Stock Client instance."""
    return _mcp_stock_client


async def get_stock_price(symbol: str) -> dict:
    """
    Get the current stock price and daily performance for a ticker symbol.
    
    Args:
        symbol: Stock ticker symbol (e.g., AAPL, GOOGL, MSFT, TSLA)
    
    Returns:
        Dictionary containing current price, daily change, and stock information
    """
    global _mcp_stock_client
    
    symbol = symbol.upper().strip()
    
    # Try MCP client first if available
    if _mcp_stock_client is not None:
        try:
            result = await _mcp_stock_client.get_stock_price(symbol)
            if result:
                return result
        except Exception as e:
            logger.error(f"MCP Stock Client error for {symbol}: {e}")
    
    # Fallback: Return error message indicating service unavailable
    return {
        "success": False,
        "error": "Stock data service is currently unavailable",
        "symbol": symbol,
        "suggestion": "Please try again later or check if the symbol is valid",
        "available_symbols": ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "NVDA", "META", "JPM", "V", "BRK-B"]
    }


async def get_market_summary() -> dict:
    """
    Get an overview of major market indices and overall market conditions.
    
    Returns:
        Dictionary containing major indices, market status, and sentiment indicators
    """
    global _mcp_stock_client
    
    # Try MCP client first if available
    if _mcp_stock_client is not None:
        try:
            result = await _mcp_stock_client.get_market_summary()
            if result:
                return result
        except Exception as e:
            logger.error(f"MCP Stock Client error for market summary: {e}")
    
    # Fallback: Return error message
    return {
        "success": False,
        "error": "Market data service is currently unavailable",
        "suggestion": "Please try again later",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S EST")
    }


async def get_stock_news(symbol: str = "") -> dict:
    """
    Get the latest financial news, optionally filtered by stock symbol.
    
    Args:
        symbol: Optional stock ticker to filter news (e.g., AAPL, TSLA)
    
    Returns:
        Dictionary containing relevant news articles and market updates
    """
    global _mcp_stock_client
    
    # Try MCP client first if available
    if _mcp_stock_client is not None:
        try:
            result = await _mcp_stock_client.get_stock_news(symbol)
            if result:
                return result
        except Exception as e:
            logger.error(f"MCP Stock Client error for news: {e}")
    
    # Fallback: Return error message
    return {
        "success": False,
        "error": "News service is currently unavailable",
        "filter": symbol if symbol else "All Markets",
        "suggestion": "Please try again later",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


# Export tools list for the agent
stock_tools = [get_stock_price, get_market_summary, get_stock_news]
