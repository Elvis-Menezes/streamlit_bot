"""
MCP Weather Client
Client for fetching weather data from Open-Meteo API.
Provides methods to fetch real weather, forecast, and air quality data.
"""

import logging
from typing import Optional, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MCPWeatherClient:
    """
    Client for fetching weather data from Open-Meteo API.
    Open-Meteo is free and doesn't require an API key.
    """
    
    WEATHER_API = "https://api.open-meteo.com/v1/forecast"
    GEOCODING_API = "https://geocoding-api.open-meteo.com/v1/search"
    AIR_QUALITY_API = "https://air-quality-api.open-meteo.com/v1/air-quality"
    
    def __init__(self):
        self._session = None
        self._initialized = False
        self._geocode_cache: Dict[str, Dict] = {}
    
    async def _get_session(self):
        """Get or create HTTP session."""
        if self._session is None:
            try:
                import httpx
                self._session = httpx.AsyncClient(timeout=30.0)
                self._initialized = True
                logger.info("MCPWeatherClient HTTP session initialized")
            except ImportError:
                logger.error("httpx not installed. Run: pip install httpx")
                return None
        return self._session
    
    async def _geocode_city(self, city: str) -> Optional[Dict]:
        """Get coordinates for a city name."""
        city_lower = city.lower().strip()
        if city_lower in self._geocode_cache:
            return self._geocode_cache[city_lower]
        
        session = await self._get_session()
        if not session:
            return None
        
        try:
            response = await session.get(
                self.GEOCODING_API,
                params={"name": city, "count": 1, "language": "en", "format": "json"}
            )
            response.raise_for_status()
            data = response.json()
            
            results = data.get("results", [])
            if not results:
                logger.warning(f"City not found: {city}")
                return None
            
            location = results[0]
            result = {
                "latitude": location.get("latitude"),
                "longitude": location.get("longitude"),
                "name": location.get("name"),
                "country": location.get("country"),
                "timezone": location.get("timezone", "UTC"),
                "admin1": location.get("admin1", ""),
            }
            
            self._geocode_cache[city_lower] = result
            logger.info(f"Geocoded {city}: {result['name']}, {result['country']}")
            return result
            
        except Exception as e:
            logger.error(f"Geocoding failed for {city}: {e}")
            return None
    
    async def get_current_weather(self, city: str) -> Optional[Dict]:
        """Get current weather for a city."""
        location = await self._geocode_city(city)
        if not location:
            return None
        
        session = await self._get_session()
        if not session:
            return None
        
        try:
            response = await session.get(
                self.WEATHER_API,
                params={
                    "latitude": location["latitude"],
                    "longitude": location["longitude"],
                    "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m,wind_direction_10m,uv_index,visibility",
                    "timezone": location["timezone"]
                }
            )
            response.raise_for_status()
            data = response.json()
            data["city"] = location["name"]
            data["country"] = location["country"]
            data["timezone"] = location["timezone"]
            logger.info(f"Fetched current weather for {city}")
            return data
        except Exception as e:
            logger.error(f"Current weather fetch failed for {city}: {e}")
            return None
    
    async def get_forecast(self, city: str, days: int = 3) -> Optional[Dict]:
        """Get weather forecast for a city."""
        location = await self._geocode_city(city)
        if not location:
            return None
        
        session = await self._get_session()
        if not session:
            return None
        
        days = min(max(days, 1), 7)
        
        try:
            response = await session.get(
                self.WEATHER_API,
                params={
                    "latitude": location["latitude"],
                    "longitude": location["longitude"],
                    "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m,wind_direction_10m,uv_index,visibility",
                    "hourly": "temperature_2m,weather_code,precipitation_probability",
                    "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max,sunrise,sunset,uv_index_max",
                    "timezone": location["timezone"],
                    "forecast_days": days
                }
            )
            response.raise_for_status()
            data = response.json()
            data["city"] = location["name"]
            data["country"] = location["country"]
            data["timezone"] = location["timezone"]
            logger.info(f"Fetched {days}-day forecast for {city}")
            return data
        except Exception as e:
            logger.error(f"Forecast fetch failed for {city}: {e}")
            return None
    
    async def get_air_quality(self, city: str) -> Optional[Dict]:
        """Get air quality data for a city."""
        location = await self._geocode_city(city)
        if not location:
            return None
        
        session = await self._get_session()
        if not session:
            return None
        
        try:
            response = await session.get(
                self.AIR_QUALITY_API,
                params={
                    "latitude": location["latitude"],
                    "longitude": location["longitude"],
                    "current": "european_aqi,us_aqi,pm10,pm2_5,carbon_monoxide,nitrogen_dioxide,ozone,dust,uv_index",
                    "timezone": location["timezone"]
                }
            )
            response.raise_for_status()
            data = response.json()
            data["city"] = location["name"]
            data["country"] = location["country"]
            data["timezone"] = location["timezone"]
            logger.info(f"Fetched air quality for {city}")
            return data
        except Exception as e:
            logger.error(f"Air quality fetch failed for {city}: {e}")
            return None
    
    async def close(self):
        """Close HTTP session."""
        if self._session:
            await self._session.aclose()
            self._session = None
            self._initialized = False
            logger.info("MCPWeatherClient session closed")


_weather_client: Optional[MCPWeatherClient] = None


def get_weather_client() -> MCPWeatherClient:
    """Get the singleton MCP Weather Client instance."""
    global _weather_client
    if _weather_client is None:
        _weather_client = MCPWeatherClient()
    return _weather_client


def shutdown_weather_client():
    """Shutdown the global weather client."""
    global _weather_client
    if _weather_client is not None:
        _weather_client = None
        logger.info("Weather client reference cleared")
