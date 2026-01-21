"""
MCP Stock Client
Client for fetching stock data from Yahoo Finance API.
Provides methods to fetch real stock prices, market summaries, and financial news.
"""

import logging
from typing import Optional, Dict, List
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MCPStockClient:
    """
    Client for fetching stock data from Yahoo Finance.
    Uses yfinance library for real market data.
    """
    
    # Major market indices
    INDICES = {
        "S&P 500": "^GSPC",
        "NASDAQ": "^IXIC",
        "DOW Jones": "^DJI",
        "Russell 2000": "^RUT",
    }
    
    # Popular stocks for quick lookup
    POPULAR_STOCKS = [
        "AAPL", "GOOGL", "MSFT", "TSLA", "AMZN",
        "NVDA", "META", "JPM", "V", "BRK-B"
    ]
    
    def __init__(self):
        self._yf = None
        self._initialized = False
        self._cache: Dict[str, Dict] = {}
        self._cache_ttl = 60  # Cache TTL in seconds
    
    def _get_yfinance(self):
        """Lazy load yfinance module."""
        if self._yf is None:
            try:
                import yfinance as yf
                self._yf = yf
                self._initialized = True
                logger.info("MCPStockClient yfinance module loaded")
            except ImportError:
                logger.error("yfinance not installed. Run: pip install yfinance")
                return None
        return self._yf
    
    def _is_market_open(self) -> bool:
        """Check if US market is currently open (simplified check)."""
        now = datetime.now()
        # NYSE/NASDAQ hours: 9:30 AM - 4:00 PM ET (simplified)
        hour = now.hour
        minute = now.minute
        weekday = now.weekday()
        
        # Weekend check
        if weekday >= 5:
            return False
        
        # Time check (simplified - assumes local time is ET)
        if hour < 9 or hour >= 16:
            return False
        if hour == 9 and minute < 30:
            return False
        
        return True
    
    async def get_stock_price(self, symbol: str) -> Optional[Dict]:
        """
        Get current stock price and daily performance for a ticker symbol.
        
        Args:
            symbol: Stock ticker symbol (e.g., AAPL, GOOGL, MSFT)
            
        Returns:
            Dictionary containing current price, daily change, and stock information
        """
        yf = self._get_yfinance()
        if not yf:
            return None
        
        symbol = symbol.upper().strip()
        # Handle BRK.B -> BRK-B conversion for Yahoo Finance
        yahoo_symbol = symbol.replace(".", "-")
        
        try:
            ticker = yf.Ticker(yahoo_symbol)
            info = ticker.info
            
            # Check if we got valid data
            if not info or info.get("regularMarketPrice") is None:
                logger.warning(f"No data found for symbol: {symbol}")
                return {
                    "success": False,
                    "error": f"Symbol '{symbol}' not found or no data available",
                    "suggestion": "Try one of these popular symbols:",
                    "available_symbols": self.POPULAR_STOCKS,
                    "tip": "Make sure to enter a valid NYSE/NASDAQ ticker symbol"
                }
            
            # Extract price data
            current_price = info.get("regularMarketPrice", 0)
            previous_close = info.get("previousClose", current_price)
            change_amount = round(current_price - previous_close, 2)
            change_percent = round((change_amount / previous_close) * 100, 2) if previous_close else 0
            
            # Get additional info
            company_name = info.get("shortName") or info.get("longName") or symbol
            sector = info.get("sector", "N/A")
            pe_ratio = info.get("trailingPE") or info.get("forwardPE") or "N/A"
            market_cap = info.get("marketCap", 0)
            volume = info.get("volume", 0)
            
            # Format market cap
            if market_cap >= 1e12:
                market_cap_str = f"${market_cap/1e12:.2f}T"
            elif market_cap >= 1e9:
                market_cap_str = f"${market_cap/1e9:.2f}B"
            elif market_cap >= 1e6:
                market_cap_str = f"${market_cap/1e6:.2f}M"
            else:
                market_cap_str = f"${market_cap:,.0f}"
            
            # Format volume
            if volume >= 1e6:
                volume_str = f"{volume/1e6:.1f}M shares"
            elif volume >= 1e3:
                volume_str = f"{volume/1e3:.1f}K shares"
            else:
                volume_str = f"{volume:,} shares"
            
            is_market_open = self._is_market_open()
            
            result = {
                "success": True,
                "symbol": symbol,
                "company_name": company_name,
                "current_price": f"${current_price:,.2f}",
                "price_change": f"{'+'if change_amount >= 0 else ''}{change_amount:,.2f}",
                "change_percent": f"{'+'if change_percent >= 0 else ''}{change_percent:.2f}%",
                "trend": "📈 Up" if change_amount >= 0 else "📉 Down",
                "sector": sector,
                "pe_ratio": f"{pe_ratio:.2f}" if isinstance(pe_ratio, (int, float)) else pe_ratio,
                "market_cap": market_cap_str,
                "volume": volume_str,
                "day_high": f"${info.get('dayHigh', 0):,.2f}",
                "day_low": f"${info.get('dayLow', 0):,.2f}",
                "52_week_high": f"${info.get('fiftyTwoWeekHigh', 0):,.2f}",
                "52_week_low": f"${info.get('fiftyTwoWeekLow', 0):,.2f}",
                "market_status": "🟢 Market Open" if is_market_open else "🔴 Market Closed",
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S EST"),
                "data_source": "Yahoo Finance"
            }
            
            logger.info(f"Fetched stock price for {symbol}: ${current_price}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to fetch stock price for {symbol}: {e}")
            return {
                "success": False,
                "error": f"Failed to fetch data for '{symbol}': {str(e)}",
                "suggestion": "Try one of these popular symbols:",
                "available_symbols": self.POPULAR_STOCKS
            }
    
    async def get_market_summary(self) -> Optional[Dict]:
        """
        Get an overview of major market indices and overall market conditions.
        
        Returns:
            Dictionary containing major indices, market status, and sentiment indicators
        """
        yf = self._get_yfinance()
        if not yf:
            return None
        
        try:
            indices_data = {}
            overall_trend = 0
            successful_fetches = 0
            
            for name, symbol in self.INDICES.items():
                try:
                    ticker = yf.Ticker(symbol)
                    info = ticker.info
                    
                    current_value = info.get("regularMarketPrice", 0)
                    previous_close = info.get("previousClose", current_value)
                    
                    if current_value and previous_close:
                        change_value = current_value - previous_close
                        change_percent = (change_value / previous_close) * 100
                        overall_trend += change_percent
                        successful_fetches += 1
                        
                        indices_data[name] = {
                            "value": f"{current_value:,.2f}",
                            "change": f"{'+'if change_percent >= 0 else ''}{change_percent:.2f}%",
                            "change_points": f"{'+'if change_value >= 0 else ''}{change_value:,.2f}",
                            "trend": "📈" if change_percent >= 0 else "📉"
                        }
                except Exception as e:
                    logger.warning(f"Failed to fetch index {name}: {e}")
                    indices_data[name] = {
                        "value": "N/A",
                        "change": "N/A",
                        "trend": "❓"
                    }
            
            # Calculate market sentiment
            if successful_fetches > 0:
                avg_trend = overall_trend / successful_fetches
                if avg_trend > 0.5:
                    sentiment = "🟢 Bullish"
                    sentiment_desc = "Markets showing positive momentum"
                elif avg_trend < -0.5:
                    sentiment = "🔴 Bearish"
                    sentiment_desc = "Markets under pressure"
                else:
                    sentiment = "🟡 Neutral"
                    sentiment_desc = "Markets trading mixed"
            else:
                sentiment = "❓ Unknown"
                sentiment_desc = "Unable to determine market sentiment"
            
            # Get VIX (Volatility Index)
            vix_value = "N/A"
            try:
                vix = yf.Ticker("^VIX")
                vix_info = vix.info
                vix_price = vix_info.get("regularMarketPrice")
                if vix_price:
                    vix_value = f"{vix_price:.2f}"
            except Exception:
                pass
            
            is_market_open = self._is_market_open()
            
            result = {
                "success": True,
                "market_status": "🟢 Market Open" if is_market_open else "🔴 Market Closed",
                "trading_session": "Regular Hours" if is_market_open else "After Hours",
                "indices": indices_data,
                "market_sentiment": sentiment,
                "sentiment_description": sentiment_desc,
                "vix_level": vix_value,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S EST"),
                "data_source": "Yahoo Finance"
            }
            
            logger.info("Fetched market summary successfully")
            return result
            
        except Exception as e:
            logger.error(f"Failed to fetch market summary: {e}")
            return {
                "success": False,
                "error": f"Failed to fetch market summary: {str(e)}"
            }
    
    async def get_stock_news(self, symbol: str = "") -> Optional[Dict]:
        """
        Get the latest financial news, optionally filtered by stock symbol.
        
        Args:
            symbol: Optional stock ticker to filter news (e.g., AAPL, TSLA)
            
        Returns:
            Dictionary containing relevant news articles and market updates
        """
        yf = self._get_yfinance()
        if not yf:
            return None
        
        try:
            news_items = []
            filter_applied = "All Markets"
            
            if symbol:
                symbol = symbol.upper().strip()
                yahoo_symbol = symbol.replace(".", "-")
                filter_applied = symbol
                
                try:
                    ticker = yf.Ticker(yahoo_symbol)
                    news = ticker.news
                    
                    if news:
                        for item in news[:10]:  # Limit to 10 news items
                            # Calculate time ago
                            pub_time = item.get("providerPublishTime", 0)
                            if pub_time:
                                time_diff = datetime.now().timestamp() - pub_time
                                if time_diff < 3600:
                                    time_ago = f"{int(time_diff/60)} minutes ago"
                                elif time_diff < 86400:
                                    time_ago = f"{int(time_diff/3600)} hours ago"
                                else:
                                    time_ago = f"{int(time_diff/86400)} days ago"
                            else:
                                time_ago = "Recently"
                            
                            news_items.append({
                                "headline": item.get("title", "No title"),
                                "source": item.get("publisher", "Unknown"),
                                "time": time_ago,
                                "link": item.get("link", ""),
                                "type": item.get("type", "STORY")
                            })
                except Exception as e:
                    logger.warning(f"Failed to fetch news for {symbol}: {e}")
                    filter_applied = f"{symbol} (news unavailable, showing general)"
            
            # If no symbol-specific news or no symbol provided, get general market news
            if not news_items:
                # Get news from major indices/ETFs for general market news
                general_symbols = ["SPY", "QQQ", "DIA"]
                
                for gen_symbol in general_symbols:
                    try:
                        ticker = yf.Ticker(gen_symbol)
                        news = ticker.news
                        
                        if news:
                            for item in news[:3]:  # Get top 3 from each
                                pub_time = item.get("providerPublishTime", 0)
                                if pub_time:
                                    time_diff = datetime.now().timestamp() - pub_time
                                    if time_diff < 3600:
                                        time_ago = f"{int(time_diff/60)} minutes ago"
                                    elif time_diff < 86400:
                                        time_ago = f"{int(time_diff/3600)} hours ago"
                                    else:
                                        time_ago = f"{int(time_diff/86400)} days ago"
                                else:
                                    time_ago = "Recently"
                                
                                news_items.append({
                                    "headline": item.get("title", "No title"),
                                    "source": item.get("publisher", "Unknown"),
                                    "time": time_ago,
                                    "link": item.get("link", ""),
                                    "type": item.get("type", "STORY")
                                })
                    except Exception:
                        pass
                
                if not symbol:
                    filter_applied = "General Market News"
            
            # Remove duplicates based on headline
            seen_headlines = set()
            unique_news = []
            for item in news_items:
                if item["headline"] not in seen_headlines:
                    seen_headlines.add(item["headline"])
                    unique_news.append(item)
            
            result = {
                "success": True,
                "filter": filter_applied,
                "article_count": len(unique_news),
                "news": unique_news[:10],  # Limit to 10
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "data_source": "Yahoo Finance",
                "disclaimer": "News is for informational purposes only. Not financial advice."
            }
            
            logger.info(f"Fetched {len(unique_news)} news articles for filter: {filter_applied}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to fetch stock news: {e}")
            return {
                "success": False,
                "error": f"Failed to fetch news: {str(e)}"
            }
    
    def close(self):
        """Clean up resources."""
        self._yf = None
        self._initialized = False
        self._cache.clear()
        logger.info("MCPStockClient resources cleaned up")


# Singleton instance
_stock_client: Optional[MCPStockClient] = None


def get_stock_client() -> MCPStockClient:
    """Get the singleton MCP Stock Client instance."""
    global _stock_client
    if _stock_client is None:
        _stock_client = MCPStockClient()
    return _stock_client


def shutdown_stock_client():
    """Shutdown the global stock client."""
    global _stock_client
    if _stock_client is not None:
        _stock_client.close()
        _stock_client = None
        logger.info("Stock client reference cleared")
