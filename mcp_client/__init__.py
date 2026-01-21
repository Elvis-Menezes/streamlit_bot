"""
MCP Client Module
Provides client wrappers for MCP servers used in the multi-agent chatbot.
"""

from .weather_client import MCPWeatherClient, get_weather_client, shutdown_weather_client
from .stock_client import MCPStockClient, get_stock_client, shutdown_stock_client

__all__ = [
    "MCPWeatherClient",
    "get_weather_client",
    "shutdown_weather_client",
    "MCPStockClient",
    "get_stock_client",
    "shutdown_stock_client",
]
