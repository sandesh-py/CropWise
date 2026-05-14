import os
import random
import httpx
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from core.config import Settings


class WeatherService:
    """Service for retrieving weather data from OpenWeather API"""
    
    def __init__(self):
        self.settings = Settings()
        self.base_url = "https://api.openweathermap.org/data/2.5"
        # Updated coordinates for Mysuru
        self.default_lat = 12.2958  # Mysuru latitude
        self.default_lon = 76.6394  # Mysuru longitude
        self.default_city = "Mysuru"
    
    def get_current_weather(self, lat: float = None, lon: float = None, city: str = None) -> Dict[str, Any]:
        """Get current weather for a location"""
        lat = lat or self.default_lat
        lon = lon or self.default_lon
        city_name = city or self.default_city
        
        # Use mock data if API key is not available
        if not self.settings.openweather_api_key:
            return self._mock_weather_data(city_name)
        
        try:
            with httpx.Client() as client:
                response = client.get(
                    f"{self.base_url}/weather",
                    params={
                        "lat": lat,
                        "lon": lon,
                        "appid": self.settings.openweather_api_key,
                        "units": "metric"
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "temperature": data["main"]["temp"],
                        "humidity": data["main"]["humidity"],
                        "pressure": data["main"]["pressure"],
                        "wind_speed": data["wind"]["speed"],
                        "description": data["weather"][0]["description"],
                        "icon": data["weather"][0]["icon"],
                        "location": {
                            "lat": lat,
                            "lon": lon,
                            "name": data["name"]
                        },
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    # Fallback to mock data if API call fails
                    return self._mock_weather_data()
        except Exception:
            # Fallback to mock data if API call fails
            return self._mock_weather_data()
    
    def get_forecast(self, lat: float = None, lon: float = None, days: int = 7) -> Dict[str, Any]:
        """Get weather forecast for a location"""
        lat = lat or self.default_lat
        lon = lon or self.default_lon
        
        # Use mock data if API key is not available
        if not self.settings.openweather_api_key:
            return self._mock_forecast_data(days)
        
        try:
            with httpx.Client() as client:
                response = client.get(
                    f"{self.base_url}/forecast",
                    params={
                        "lat": lat,
                        "lon": lon,
                        "appid": self.settings.openweather_api_key,
                        "units": "metric",
                        "cnt": days * 8  # 8 forecasts per day (3-hour intervals)
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    forecasts = []
                    
                    for item in data["list"]:
                        forecasts.append({
                            "timestamp": item["dt_txt"],
                            "temperature": item["main"]["temp"],
                            "humidity": item["main"]["humidity"],
                            "pressure": item["main"]["pressure"],
                            "wind_speed": item["wind"]["speed"],
                            "description": item["weather"][0]["description"],
                            "icon": item["weather"][0]["icon"],
                            "rain": item.get("rain", {}).get("3h", 0)
                        })
                    
                    return {
                        "forecast": forecasts,
                        "location": {
                            "lat": lat,
                            "lon": lon,
                            "name": data["city"]["name"]
                        }
                    }
                else:
                    # Fallback to mock data if API call fails
                    return self._mock_forecast_data(days)
        except Exception:
            # Fallback to mock data if API call fails
            return self._mock_forecast_data(days)
    
    def _mock_weather_data(self, city_name: str = "Mysuru") -> Dict[str, Any]:
        """Generate mock weather data for testing"""
        # Mysuru-specific mock data
        if city_name.lower() == "mysuru":
            return {
                "temperature": round(random.uniform(22.0, 32.0), 1),  # Mysuru typical range
                "humidity": random.randint(60, 85),  # Higher humidity in Mysuru
                "pressure": random.randint(1008, 1015),
                "wind_speed": round(random.uniform(1.0, 5.0), 1),
                "description": random.choice(["clear sky", "few clouds", "scattered clouds", "light rain"]),
                "icon": random.choice(["01d", "02d", "03d", "10d"]),
                "location": {
                    "lat": self.default_lat,
                    "lon": self.default_lon,
                    "name": "Mysuru",
                    "country": "IN"
                },
                "rainfall": round(random.uniform(0, 15.0), 1),  # Rainfall in mm
                "timestamp": datetime.now().isoformat()
            }
        else:
            # Generic mock data for other locations
            return {
                "temperature": round(random.uniform(15.0, 35.0), 1),
                "humidity": random.randint(40, 90),
                "pressure": random.randint(1000, 1020),
                "wind_speed": round(random.uniform(0.5, 10.0), 1),
                "description": random.choice(["clear sky", "few clouds", "scattered clouds", "light rain", "heavy rain"]),
                "icon": random.choice(["01d", "02d", "03d", "10d", "11d"]),
                "location": {
                    "lat": self.default_lat,
                    "lon": self.default_lon,
                    "name": city_name,
                    "country": "Unknown"
                },
                "rainfall": round(random.uniform(0, 25.0), 1),
                "timestamp": datetime.now().isoformat()
            }
    
    def _mock_forecast_data(self, days: int = 7) -> Dict[str, Any]:
        """Generate mock forecast data for Mysuru region"""
        forecasts = []
        
        # Mysuru typical weather patterns by season
        now = datetime.now()
        
        # Generate forecast for each day
        for day in range(days):
            # Generate 8 forecasts per day (3-hour intervals)
            for hour in [0, 3, 6, 9, 12, 15, 18, 21]:
                forecast_time = now + timedelta(days=day, hours=hour)
                
                # Temperature varies by time of day
                if 6 <= hour < 12:  # Morning
                    temp = random.uniform(24.0, 28.0)
                elif 12 <= hour < 18:  # Afternoon
                    temp = random.uniform(28.0, 32.0)
                else:  # Evening/Night
                    temp = random.uniform(20.0, 24.0)
                
                # Humidity is generally higher at night and early morning
                if 0 <= hour < 9:
                    humidity = random.uniform(75.0, 90.0)
                else:
                    humidity = random.uniform(60.0, 75.0)
                
                # Rain is more likely in afternoon
                rain_chance = 0.3 if 12 <= hour < 18 else 0.1
                rain = random.uniform(0.0, 5.0) if random.random() < rain_chance else 0.0
                
                descriptions = [
                    "clear sky", "few clouds", "scattered clouds", 
                    "broken clouds", "light rain", "moderate rain"
                ]
                
                icons = ["01d", "02d", "03d", "04d", "09d", "10d"]
                
                # More clouds and rain in afternoon
                if rain > 0:
                    description_idx = random.randint(4, 5)
                else:
                    description_idx = random.randint(0, 3)
                
                forecasts.append({
                    "timestamp": forecast_time.isoformat(),
                    "temperature": round(temp, 1),
                    "humidity": round(humidity, 1),
                    "pressure": random.randint(1008, 1020),
                    "wind_speed": round(random.uniform(1.0, 5.0), 1),
                    "description": descriptions[description_idx],
                    "icon": icons[description_idx],
                    "rain": round(rain, 1)
                })
        
        return {
            "forecast": forecasts,
            "location": {
                "lat": self.default_lat,
                "lon": self.default_lon,
                "name": "Mysuru"
            }
        }


# Create a singleton instance for use throughout the application
weather_service = WeatherService()
