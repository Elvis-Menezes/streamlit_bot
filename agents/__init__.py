"""
Multi-Agent Configuration Module
Exports all agent configurations and tools for the chatbot.
"""

from .ecommerce import ECOMMERCE_CONFIG, ecommerce_tools
from .stock import STOCK_CONFIG, stock_tools
from .weather import WEATHER_CONFIG, weather_tools

# Agent registry - maps agent IDs to their configurations
AGENTS = {
    "ecommerce": ECOMMERCE_CONFIG,
    "stock": STOCK_CONFIG,
    "weather": WEATHER_CONFIG,
}

# Tools registry - maps agent IDs to their available tools
TOOLS = {
    "ecommerce": ecommerce_tools,
    "stock": stock_tools,
    "weather": weather_tools,
}

__all__ = ["AGENTS", "TOOLS"]
