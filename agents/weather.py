"""
Weather Agent - SkyWatch for GlobalWeather Services
Provides weather forecasts, alerts, and air quality information.
"""

import random
from datetime import datetime, timedelta

# Agent Configuration
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
- Provide accurate weather forecasts for any city
- Alert users about severe weather conditions
- Share air quality information and health recommendations
- Help users plan outdoor activities based on weather

Always include:
- The data source and last update time
- Practical tips based on the weather conditions
- Temperature in Fahrenheit (you can mention Celsius too if asked)"""
}

# Weather conditions with icons
WEATHER_CONDITIONS = {
    "Sunny": {"icon": "☀️", "outdoor_score": 10},
    "Partly Cloudy": {"icon": "⛅", "outdoor_score": 8},
    "Cloudy": {"icon": "☁️", "outdoor_score": 6},
    "Overcast": {"icon": "🌥️", "outdoor_score": 5},
    "Light Rain": {"icon": "🌦️", "outdoor_score": 3},
    "Rainy": {"icon": "🌧️", "outdoor_score": 2},
    "Thunderstorm": {"icon": "⛈️", "outdoor_score": 1},
    "Snow": {"icon": "🌨️", "outdoor_score": 4},
    "Clear": {"icon": "🌙", "outdoor_score": 9},
    "Foggy": {"icon": "🌫️", "outdoor_score": 4},
}

# City base weather data
CITIES_WEATHER = {
    "new york": {"temp": 42, "condition": "Cloudy", "humidity": 65, "wind": 12, "timezone": "EST"},
    "los angeles": {"temp": 72, "condition": "Sunny", "humidity": 35, "wind": 8, "timezone": "PST"},
    "chicago": {"temp": 35, "condition": "Snow", "humidity": 80, "wind": 18, "timezone": "CST"},
    "miami": {"temp": 78, "condition": "Partly Cloudy", "humidity": 70, "wind": 10, "timezone": "EST"},
    "seattle": {"temp": 48, "condition": "Rainy", "humidity": 85, "wind": 14, "timezone": "PST"},
    "denver": {"temp": 45, "condition": "Clear", "humidity": 30, "wind": 6, "timezone": "MST"},
    "boston": {"temp": 38, "condition": "Cloudy", "humidity": 72, "wind": 15, "timezone": "EST"},
    "san francisco": {"temp": 58, "condition": "Foggy", "humidity": 78, "wind": 12, "timezone": "PST"},
    "london": {"temp": 45, "condition": "Overcast", "humidity": 75, "wind": 15, "timezone": "GMT"},
    "tokyo": {"temp": 55, "condition": "Clear", "humidity": 50, "wind": 8, "timezone": "JST"},
    "paris": {"temp": 48, "condition": "Cloudy", "humidity": 70, "wind": 12, "timezone": "CET"},
    "sydney": {"temp": 82, "condition": "Sunny", "humidity": 55, "wind": 10, "timezone": "AEST"},
    "toronto": {"temp": 32, "condition": "Snow", "humidity": 78, "wind": 16, "timezone": "EST"},
    "dubai": {"temp": 85, "condition": "Sunny", "humidity": 40, "wind": 8, "timezone": "GST"},
    "singapore": {"temp": 88, "condition": "Partly Cloudy", "humidity": 82, "wind": 6, "timezone": "SGT"},
}

# Weather alerts by city
WEATHER_ALERTS = {
    "chicago": {
        "type": "Winter Storm Warning",
        "severity": "Moderate",
        "icon": "🌨️",
        "message": "Heavy snow expected. Accumulation of 4-6 inches possible.",
        "advice": "Limit travel. Keep emergency supplies ready.",
        "expires": "Tomorrow 6:00 PM CST"
    },
    "miami": {
        "type": "Heat Advisory",
        "severity": "Low",
        "icon": "🌡️",
        "message": "High temperatures and humidity expected.",
        "advice": "Stay hydrated. Limit outdoor activities during peak hours.",
        "expires": "Today 8:00 PM EST"
    },
    "seattle": {
        "type": "Flood Watch",
        "severity": "Moderate",
        "icon": "🌊",
        "message": "Heavy rain may cause localized flooding in low-lying areas.",
        "advice": "Avoid flood-prone areas. Do not drive through standing water.",
        "expires": "Tomorrow 12:00 PM PST"
    },
    "denver": {
        "type": "Wind Advisory",
        "severity": "Low",
        "icon": "💨",
        "message": "Strong winds expected with gusts up to 45 mph.",
        "advice": "Secure outdoor objects. Use caution when driving high-profile vehicles.",
        "expires": "Tonight 10:00 PM MST"
    },
}


async def get_weather_forecast(city: str, days: int = 3) -> dict:
    """
    Get the current weather and forecast for a specific city.
    
    Args:
        city: City name (e.g., New York, London, Tokyo, Miami)
        days: Number of forecast days (1-7, default is 3)
    
    Returns:
        Dictionary containing current conditions and multi-day forecast
    """
    city_lower = city.lower().strip()
    days = min(max(days, 1), 7)  # Clamp between 1-7
    
    # Get base weather or generate for unknown city
    if city_lower in CITIES_WEATHER:
        base = CITIES_WEATHER[city_lower]
    else:
        # Generate reasonable random weather for unknown cities
        conditions = list(WEATHER_CONDITIONS.keys())
        base = {
            "temp": random.randint(35, 85),
            "condition": random.choice(conditions[:6]),  # Exclude extreme conditions
            "humidity": random.randint(30, 80),
            "wind": random.randint(5, 20),
            "timezone": "UTC"
        }
    
    # Get condition details
    condition_info = WEATHER_CONDITIONS.get(base["condition"], {"icon": "🌡️", "outdoor_score": 5})
    
    # Generate forecast
    forecast = []
    for i in range(days):
        date = datetime.now() + timedelta(days=i)
        temp_variation = random.randint(-8, 8)
        high_temp = base["temp"] + random.randint(8, 15) + temp_variation
        low_temp = base["temp"] - random.randint(5, 12) + temp_variation
        
        # Vary conditions slightly
        if i == 0:
            day_condition = base["condition"]
        else:
            conditions = list(WEATHER_CONDITIONS.keys())
            day_condition = random.choice(conditions[:7])
        
        day_info = WEATHER_CONDITIONS.get(day_condition, {"icon": "🌡️", "outdoor_score": 5})
        precip_chance = random.randint(0, 70) if "Rain" in day_condition or "Storm" in day_condition else random.randint(0, 30)
        
        forecast.append({
            "day": "Today" if i == 0 else date.strftime("%A"),
            "date": date.strftime("%b %d"),
            "condition": f"{day_info['icon']} {day_condition}",
            "high": f"{high_temp}°F",
            "low": f"{low_temp}°F",
            "precipitation": f"{precip_chance}%",
            "outdoor_score": f"{day_info['outdoor_score']}/10"
        })
    
    # Generate activity recommendation
    outdoor_score = condition_info["outdoor_score"]
    if outdoor_score >= 8:
        activity_tip = "Perfect weather for outdoor activities! 🏃‍♂️"
    elif outdoor_score >= 5:
        activity_tip = "Decent conditions for outdoor plans. Consider bringing layers."
    else:
        activity_tip = "Indoor activities recommended. Stay cozy! 🏠"
    
    feels_like = base["temp"] - (base["wind"] // 3) + random.randint(-3, 3)
    
    return {
        "success": True,
        "city": city.title(),
        "current": {
            "condition": f"{condition_info['icon']} {base['condition']}",
            "temperature": f"{base['temp']}°F ({round((base['temp']-32)*5/9)}°C)",
            "feels_like": f"{feels_like}°F",
            "humidity": f"{base['humidity']}%",
            "wind": f"{base['wind']} mph",
            "uv_index": random.randint(1, 10),
            "visibility": f"{random.randint(5, 10)} miles"
        },
        "forecast": forecast,
        "activity_recommendation": activity_tip,
        "sunrise": "6:52 AM",
        "sunset": "5:28 PM",
        "timezone": base.get("timezone", "UTC"),
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "source": "GlobalWeather Services"
    }


async def get_weather_alerts(city: str) -> dict:
    """
    Check for active weather alerts and warnings in a specific area.
    
    Args:
        city: City name to check for weather alerts
    
    Returns:
        Dictionary containing any active alerts, their severity, and safety recommendations
    """
    city_lower = city.lower().strip()
    
    if city_lower in WEATHER_ALERTS:
        alert = WEATHER_ALERTS[city_lower]
        return {
            "success": True,
            "city": city.title(),
            "has_alerts": True,
            "alert_count": 1,
            "alerts": [{
                "type": f"{alert['icon']} {alert['type']}",
                "severity": alert["severity"],
                "message": alert["message"],
                "safety_advice": alert["advice"],
                "expires": alert["expires"]
            }],
            "emergency_contacts": {
                "emergency": "911",
                "weather_hotline": "1-800-WEATHER"
            },
            "checked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    return {
        "success": True,
        "city": city.title(),
        "has_alerts": False,
        "alert_count": 0,
        "message": "✅ No active weather alerts for this area.",
        "status": "All Clear",
        "tip": "Weather conditions are normal. Enjoy your day!",
        "checked_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


async def get_air_quality(city: str) -> dict:
    """
    Get the Air Quality Index (AQI) and health recommendations for a city.
    
    Args:
        city: City name to check air quality
    
    Returns:
        Dictionary containing AQI value, category, pollutants, and health advice
    """
    city_lower = city.lower().strip()
    
    # Predefined AQI for some cities
    city_aqi = {
        "new york": 52,
        "los angeles": 78,
        "chicago": 45,
        "denver": 35,
        "seattle": 28,
        "miami": 38,
        "beijing": 156,
        "delhi": 185,
        "london": 42,
        "paris": 48,
        "tokyo": 55,
        "sydney": 25,
    }
    
    aqi = city_aqi.get(city_lower, random.randint(20, 90))
    
    # Determine AQI category and recommendations
    if aqi <= 50:
        category = "Good"
        color = "🟢"
        health_message = "Air quality is excellent! Great day for outdoor activities."
        sensitive_groups = "No restrictions"
        outdoor_exercise = "Recommended"
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
    else:
        category = "Very Unhealthy"
        color = "🟣"
        health_message = "Health alert: everyone may experience serious health effects."
        sensitive_groups = "Stay indoors"
        outdoor_exercise = "Avoid all outdoor physical activity"
    
    # Common pollutants
    pollutants = {
        "PM2.5": f"{random.randint(5, 35)} µg/m³",
        "PM10": f"{random.randint(10, 50)} µg/m³",
        "O3 (Ozone)": f"{random.randint(20, 60)} ppb",
        "NO2": f"{random.randint(5, 30)} ppb",
        "CO": f"{random.uniform(0.1, 1.5):.1f} ppm"
    }
    
    return {
        "success": True,
        "city": city.title(),
        "aqi": aqi,
        "category": f"{color} {category}",
        "health_message": health_message,
        "recommendations": {
            "general_public": outdoor_exercise,
            "sensitive_groups": sensitive_groups,
            "mask_recommended": aqi > 100
        },
        "pollutants": pollutants,
        "dominant_pollutant": "PM2.5",
        "forecast_trend": random.choice(["Improving", "Stable", "Slightly worsening"]),
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "source": "GlobalWeather Air Quality Network"
    }


# Export tools list for the agent
weather_tools = [get_weather_forecast, get_weather_alerts, get_air_quality]
