"""
Weather Agent - SkyWatch for GlobalWeather Services
Provides weather forecasts, alerts, and air quality information.

Uses MCP Weather Server (Open-Meteo) exclusively for real weather data.
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List

# Configure logging
logger = logging.getLogger(__name__)

# =============================================================================
# Agent Configuration
# =============================================================================

WEATHER_CONFIG = {
    "id": "weather",
    "name": "SkyWatch",
    "company": "GlobalWeather Services",
    "icon": "🌤️",
    "color": "#45B7D1",
    "description": """You are SkyWatch, the helpful and friendly weather assistant for GlobalWeather Services.

Your personality:
- Warm, friendly, and genuinely helpful
- Make weather information easy to understand
- Give practical advice for planning activities
- Use weather-related emojis to make responses engaging

Your responsibilities:
- Provide accurate weather forecasts for any city using live data from Open-Meteo
- Alert users about severe weather conditions
- Share air quality information and health recommendations
- Help users plan outdoor activities based on weather

Always include:
- The data source (Open-Meteo via MCP Server)
- Practical tips based on the weather conditions
- Temperature in both Fahrenheit and Celsius"""
}

# =============================================================================
# Weather Conditions Mapping (WMO Weather Codes)
# =============================================================================

WEATHER_CONDITIONS = {
    "Clear": {"icon": "☀️", "outdoor_score": 10, "description": "Clear sky"},
    "Partly Cloudy": {"icon": "⛅", "outdoor_score": 8, "description": "Partly cloudy"},
    "Cloudy": {"icon": "☁️", "outdoor_score": 6, "description": "Cloudy"},
    "Overcast": {"icon": "🌥️", "outdoor_score": 5, "description": "Overcast"},
    "Foggy": {"icon": "🌫️", "outdoor_score": 4, "description": "Foggy conditions"},
    "Light Rain": {"icon": "🌦️", "outdoor_score": 3, "description": "Light rain"},
    "Rainy": {"icon": "🌧️", "outdoor_score": 2, "description": "Rainy"},
    "Heavy Rain": {"icon": "🌧️", "outdoor_score": 1, "description": "Heavy rain"},
    "Snow": {"icon": "🌨️", "outdoor_score": 4, "description": "Snowy"},
    "Heavy Snow": {"icon": "❄️", "outdoor_score": 2, "description": "Heavy snow"},
    "Thunderstorm": {"icon": "⛈️", "outdoor_score": 1, "description": "Thunderstorm"},
    "Unknown": {"icon": "🌡️", "outdoor_score": 5, "description": "Weather data unavailable"},
}

# WMO Weather interpretation codes mapping
WMO_WEATHER_CODES = {
    0: "Clear",
    1: "Clear",
    2: "Partly Cloudy",
    3: "Overcast",
    45: "Foggy",
    48: "Foggy",
    51: "Light Rain",
    53: "Light Rain",
    55: "Rainy",
    56: "Light Rain",
    57: "Rainy",
    61: "Light Rain",
    63: "Rainy",
    65: "Heavy Rain",
    66: "Light Rain",
    67: "Heavy Rain",
    71: "Snow",
    73: "Snow",
    75: "Heavy Snow",
    77: "Snow",
    80: "Light Rain",
    81: "Rainy",
    82: "Heavy Rain",
    85: "Snow",
    86: "Heavy Snow",
    95: "Thunderstorm",
    96: "Thunderstorm",
    99: "Thunderstorm",
}

# =============================================================================
# MCP Client Integration
# =============================================================================

def _get_mcp_client():
    """Get the MCP weather client (lazy import to avoid startup issues)."""
    try:
        from mcp_client import get_weather_client
        return get_weather_client()
    except ImportError:
        logger.error("MCP client module not found - please install mcp_client")
        return None
    except Exception as e:
        logger.error(f"Failed to get MCP client: {e}")
        return None


def _map_weather_code(code: int) -> str:
    """Map Open-Meteo WMO weather code to condition name."""
    return WMO_WEATHER_CODES.get(code, "Unknown")


def _get_condition_info(condition: str) -> Dict:
    """Get icon and outdoor score for a weather condition."""
    return WEATHER_CONDITIONS.get(condition, WEATHER_CONDITIONS["Unknown"])


def _celsius_to_fahrenheit(celsius: float) -> int:
    """Convert Celsius to Fahrenheit."""
    return round(celsius * 9/5 + 32)


def _get_activity_recommendation(outdoor_score: int, condition: str) -> str:
    """Generate activity recommendation based on weather conditions."""
    if outdoor_score >= 8:
        return "☀️ Perfect weather for outdoor activities! Enjoy hiking, cycling, or a picnic."
    elif outdoor_score >= 6:
        return "⛅ Good conditions for outdoor plans. Maybe bring a light jacket."
    elif outdoor_score >= 4:
        return "🌥️ Decent weather, but consider indoor backup plans."
    elif "Rain" in condition or "Snow" in condition:
        return "🌧️ Wet conditions - bring an umbrella or raincoat if going out."
    elif "Thunderstorm" in condition:
        return "⛈️ Stay indoors! Thunderstorms expected - avoid open areas."
    else:
        return "🏠 Indoor activities recommended today."


# =============================================================================
# Public Tool Functions
# =============================================================================

async def get_weather_forecast(city: str, days: int = 3) -> dict:
    """
    Get the current weather and forecast for a specific city using live data from Open-Meteo.
    
    Args:
        city: City name (e.g., New York, London, Tokyo, Miami)
        days: Number of forecast days (1-7, default is 3)
    
    Returns:
        Dictionary containing current conditions and multi-day forecast from Open-Meteo
    """
    days = min(max(days, 1), 7)  # Clamp between 1-7
    
    # Get MCP client
    mcp_client = _get_mcp_client()
    
    if not mcp_client:
        return {
            "success": False,
            "city": city.title(),
            "error": "Weather service unavailable",
            "message": "❌ Unable to connect to the MCP Weather Server. Please try again later.",
            "suggestion": "The weather service may be starting up. Please wait a moment and try again.",
            "checked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    try:
        # Fetch data from MCP server
        mcp_data = await mcp_client.get_forecast(city, days)
        
        if not mcp_data:
            return {
                "success": False,
                "city": city.title(),
                "error": "No data received",
                "message": f"❌ Could not retrieve weather data for '{city}'.",
                "suggestion": "Please check the city name spelling or try a major city nearby.",
                "checked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        
        # Parse current weather
        current = mcp_data.get("current", {})
        hourly = mcp_data.get("hourly", {})
        daily = mcp_data.get("daily", {})
        
        # Current conditions
        weather_code = current.get("weather_code", 0)
        condition = _map_weather_code(weather_code)
        condition_info = _get_condition_info(condition)
        
        temp_c = current.get("temperature_2m", 0)
        temp_f = _celsius_to_fahrenheit(temp_c)
        humidity = current.get("relative_humidity_2m", 0)
        wind_speed_kmh = current.get("wind_speed_10m", 0)
        wind_speed_mph = round(wind_speed_kmh * 0.621371)
        
        # Calculate feels like (simple wind chill approximation)
        feels_like_c = temp_c - (wind_speed_kmh * 0.1)
        feels_like_f = _celsius_to_fahrenheit(feels_like_c)
        
        # Build forecast from daily data
        forecast = []
        daily_times = daily.get("time", [])
        daily_weather_codes = daily.get("weather_code", [])
        daily_temp_max = daily.get("temperature_2m_max", [])
        daily_temp_min = daily.get("temperature_2m_min", [])
        daily_precip = daily.get("precipitation_probability_max", [])
        
        for i in range(min(days, len(daily_times))):
            date = datetime.strptime(daily_times[i], "%Y-%m-%d") if daily_times else datetime.now() + timedelta(days=i)
            day_code = daily_weather_codes[i] if i < len(daily_weather_codes) else 0
            day_condition = _map_weather_code(day_code)
            day_info = _get_condition_info(day_condition)
            
            high_c = daily_temp_max[i] if i < len(daily_temp_max) else temp_c + 5
            low_c = daily_temp_min[i] if i < len(daily_temp_min) else temp_c - 5
            precip = daily_precip[i] if i < len(daily_precip) else 0
            
            forecast.append({
                "day": "Today" if i == 0 else date.strftime("%A"),
                "date": date.strftime("%b %d"),
                "condition": f"{day_info['icon']} {day_condition}",
                "high": f"{_celsius_to_fahrenheit(high_c)}°F ({round(high_c)}°C)",
                "low": f"{_celsius_to_fahrenheit(low_c)}°F ({round(low_c)}°C)",
                "precipitation": f"{precip}%",
                "outdoor_score": f"{day_info['outdoor_score']}/10"
            })
        
        # Get sunrise/sunset if available
        sunrise = daily.get("sunrise", ["6:30 AM"])[0] if daily.get("sunrise") else "N/A"
        sunset = daily.get("sunset", ["6:30 PM"])[0] if daily.get("sunset") else "N/A"
        
        # Format sunrise/sunset times
        if sunrise != "N/A" and "T" in str(sunrise):
            sunrise = datetime.fromisoformat(sunrise).strftime("%I:%M %p")
        if sunset != "N/A" and "T" in str(sunset):
            sunset = datetime.fromisoformat(sunset).strftime("%I:%M %p")
        
        return {
            "success": True,
            "city": city.title(),
            "current": {
                "condition": f"{condition_info['icon']} {condition}",
                "description": condition_info["description"],
                "temperature": f"{temp_f}°F ({round(temp_c)}°C)",
                "feels_like": f"{feels_like_f}°F ({round(feels_like_c)}°C)",
                "humidity": f"{humidity}%",
                "wind": f"{wind_speed_mph} mph ({wind_speed_kmh} km/h)",
                "uv_index": current.get("uv_index", "N/A"),
                "visibility": f"{current.get('visibility', 10000) / 1000:.1f} km"
            },
            "forecast": forecast,
            "activity_recommendation": _get_activity_recommendation(condition_info["outdoor_score"], condition),
            "sunrise": sunrise,
            "sunset": sunset,
            "timezone": mcp_data.get("timezone", "UTC"),
            "coordinates": {
                "latitude": mcp_data.get("latitude", "N/A"),
                "longitude": mcp_data.get("longitude", "N/A")
            },
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "source": "Open-Meteo via MCP Server (Live Data)"
        }
        
    except Exception as e:
        logger.error(f"Weather forecast failed for {city}: {e}")
        return {
            "success": False,
            "city": city.title(),
            "error": str(e),
            "message": f"❌ Failed to retrieve weather for '{city}'.",
            "suggestion": "Please check the city name or try again later.",
            "checked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }


async def get_weather_alerts(city: str) -> dict:
    """
    Check for active weather alerts and warnings in a specific area using MCP server.
    
    Args:
        city: City name to check for weather alerts
    
    Returns:
        Dictionary containing any active alerts, their severity, and safety recommendations
    """
    # Get MCP client
    mcp_client = _get_mcp_client()
    
    if not mcp_client:
        return {
            "success": False,
            "city": city.title(),
            "error": "Alert service unavailable",
            "message": "❌ Unable to connect to the weather alert service.",
            "checked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    try:
        # Try to get alerts from MCP server
        # Note: Open-Meteo may not provide alerts, so we'll check weather conditions
        mcp_data = await mcp_client.get_current_weather(city)
        
        if not mcp_data:
            return {
                "success": False,
                "city": city.title(),
                "error": "No data received",
                "message": f"❌ Could not check alerts for '{city}'.",
                "checked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        
        # Parse current weather to determine if there are severe conditions
        current = mcp_data.get("current", {})
        weather_code = current.get("weather_code", 0)
        condition = _map_weather_code(weather_code)
        wind_speed = current.get("wind_speed_10m", 0)
        temp_c = current.get("temperature_2m", 20)
        
        alerts = []
        
        # Check for severe weather conditions
        if weather_code >= 95:  # Thunderstorm codes
            alerts.append({
                "type": "⛈️ Thunderstorm Warning",
                "severity": "High",
                "message": "Thunderstorms are occurring or expected in this area.",
                "safety_advice": "Seek shelter immediately. Avoid open areas, tall objects, and bodies of water.",
                "expires": "Until conditions improve"
            })
        
        if wind_speed > 60:  # Strong winds (>60 km/h)
            alerts.append({
                "type": "💨 High Wind Warning",
                "severity": "Moderate",
                "message": f"Strong winds of {wind_speed} km/h detected.",
                "safety_advice": "Secure loose outdoor objects. Avoid driving high-profile vehicles.",
                "expires": "Until wind subsides"
            })
        
        if temp_c > 35:  # Extreme heat (>35°C / 95°F)
            alerts.append({
                "type": "🌡️ Extreme Heat Warning",
                "severity": "Moderate",
                "message": f"Temperature of {temp_c}°C ({_celsius_to_fahrenheit(temp_c)}°F) detected.",
                "safety_advice": "Stay hydrated. Limit outdoor activities during peak heat. Check on elderly neighbors.",
                "expires": "Until temperatures drop"
            })
        
        if temp_c < -10:  # Extreme cold (<-10°C / 14°F)
            alerts.append({
                "type": "❄️ Extreme Cold Warning",
                "severity": "Moderate",
                "message": f"Temperature of {temp_c}°C ({_celsius_to_fahrenheit(temp_c)}°F) detected.",
                "safety_advice": "Dress in layers. Limit exposure to cold. Check on vulnerable individuals.",
                "expires": "Until temperatures rise"
            })
        
        if weather_code in [65, 67, 82]:  # Heavy rain
            alerts.append({
                "type": "🌧️ Heavy Rain Advisory",
                "severity": "Low",
                "message": "Heavy rainfall may cause localized flooding.",
                "safety_advice": "Avoid flood-prone areas. Do not drive through standing water.",
                "expires": "Until rain subsides"
            })
        
        if weather_code in [75, 86]:  # Heavy snow
            alerts.append({
                "type": "🌨️ Heavy Snow Advisory",
                "severity": "Moderate",
                "message": "Heavy snowfall may impact travel conditions.",
                "safety_advice": "Avoid unnecessary travel. Keep emergency supplies ready.",
                "expires": "Until snowfall ends"
            })
        
        if alerts:
            return {
                "success": True,
                "city": city.title(),
                "has_alerts": True,
                "alert_count": len(alerts),
                "alerts": alerts,
                "emergency_contacts": {
                    "emergency": "911 (US) / 112 (EU)",
                    "weather_info": "weather.gov"
                },
                "checked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "source": "Open-Meteo via MCP Server (Live Analysis)"
            }
        
        return {
            "success": True,
            "city": city.title(),
            "has_alerts": False,
            "alert_count": 0,
            "message": "✅ No active weather alerts for this area.",
            "status": "All Clear",
            "current_conditions": f"{_get_condition_info(condition)['icon']} {condition}",
            "tip": "Weather conditions are normal. Enjoy your day!",
            "checked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "source": "Open-Meteo via MCP Server (Live Analysis)"
        }
        
    except Exception as e:
        logger.error(f"Weather alerts check failed for {city}: {e}")
        return {
            "success": False,
            "city": city.title(),
            "error": str(e),
            "message": f"❌ Failed to check alerts for '{city}'.",
            "checked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }


async def get_air_quality(city: str) -> dict:
    """
    Get the Air Quality Index (AQI) and health recommendations for a city using MCP server.
    
    Args:
        city: City name to check air quality
    
    Returns:
        Dictionary containing AQI value, category, pollutants, and health advice
    """
    # Get MCP client
    mcp_client = _get_mcp_client()
    
    if not mcp_client:
        return {
            "success": False,
            "city": city.title(),
            "error": "Air quality service unavailable",
            "message": "❌ Unable to connect to the air quality service.",
            "checked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    try:
        # Fetch air quality data from MCP server
        mcp_data = await mcp_client.get_air_quality(city)
        
        if not mcp_data:
            return {
                "success": False,
                "city": city.title(),
                "error": "No data received",
                "message": f"❌ Could not retrieve air quality data for '{city}'.",
                "suggestion": "Please check the city name or try a major city nearby.",
                "checked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        
        # Parse air quality data
        current = mcp_data.get("current", mcp_data)
        
        # Get AQI - Open-Meteo uses European AQI
        aqi = current.get("european_aqi", current.get("us_aqi", current.get("aqi", 50)))
        
        # Get pollutant values
        pm25 = current.get("pm2_5", 0)
        pm10 = current.get("pm10", 0)
        ozone = current.get("ozone", current.get("o3", 0))
        no2 = current.get("nitrogen_dioxide", current.get("no2", 0))
        co = current.get("carbon_monoxide", current.get("co", 0))
        
        # Determine AQI category and recommendations
        if aqi <= 50:
            category = "Good"
            color = "🟢"
            health_message = "Air quality is excellent! Great day for outdoor activities."
            sensitive_groups = "No restrictions"
            outdoor_exercise = "Highly recommended"
        elif aqi <= 100:
            category = "Moderate"
            color = "🟡"
            health_message = "Air quality is acceptable. Sensitive individuals should consider limiting prolonged outdoor exertion."
            sensitive_groups = "May experience minor symptoms"
            outdoor_exercise = "Generally safe"
        elif aqi <= 150:
            category = "Unhealthy for Sensitive Groups"
            color = "🟠"
            health_message = "Members of sensitive groups may experience health effects. General public less likely to be affected."
            sensitive_groups = "Reduce prolonged outdoor exertion"
            outdoor_exercise = "Limit intense outdoor activity"
        elif aqi <= 200:
            category = "Unhealthy"
            color = "🔴"
            health_message = "Everyone may begin to experience health effects. Sensitive groups may experience more serious effects."
            sensitive_groups = "Avoid outdoor activities"
            outdoor_exercise = "Move activities indoors"
        elif aqi <= 300:
            category = "Very Unhealthy"
            color = "🟣"
            health_message = "Health alert: everyone may experience serious health effects."
            sensitive_groups = "Stay indoors"
            outdoor_exercise = "Avoid all outdoor physical activity"
        else:
            category = "Hazardous"
            color = "🟤"
            health_message = "Health emergency: everyone is likely to be affected."
            sensitive_groups = "Remain indoors with air filtration"
            outdoor_exercise = "Do not go outside"
        
        # Determine dominant pollutant
        pollutant_values = {"PM2.5": pm25, "PM10": pm10, "Ozone": ozone, "NO2": no2}
        dominant = max(pollutant_values, key=pollutant_values.get) if any(pollutant_values.values()) else "PM2.5"
        
        return {
            "success": True,
            "city": city.title(),
            "aqi": aqi,
            "aqi_scale": "European AQI",
            "category": f"{color} {category}",
            "health_message": health_message,
            "recommendations": {
                "general_public": outdoor_exercise,
                "sensitive_groups": sensitive_groups,
                "mask_recommended": aqi > 100,
                "windows": "Keep closed" if aqi > 150 else "Can be open"
            },
            "pollutants": {
                "PM2.5": f"{pm25:.1f} µg/m³" if pm25 else "N/A",
                "PM10": f"{pm10:.1f} µg/m³" if pm10 else "N/A",
                "Ozone (O₃)": f"{ozone:.1f} µg/m³" if ozone else "N/A",
                "NO₂": f"{no2:.1f} µg/m³" if no2 else "N/A",
                "CO": f"{co:.1f} µg/m³" if co else "N/A"
            },
            "dominant_pollutant": dominant,
            "coordinates": {
                "latitude": mcp_data.get("latitude", "N/A"),
                "longitude": mcp_data.get("longitude", "N/A")
            },
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "source": "Open-Meteo Air Quality via MCP Server (Live Data)"
        }
        
    except Exception as e:
        logger.error(f"Air quality check failed for {city}: {e}")
        return {
            "success": False,
            "city": city.title(),
            "error": str(e),
            "message": f"❌ Failed to retrieve air quality for '{city}'.",
            "suggestion": "Please check the city name or try again later.",
            "checked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }


# =============================================================================
# Export Tools
# =============================================================================

weather_tools = [get_weather_forecast, get_weather_alerts, get_air_quality]
