import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
import json
from pathlib import Path
import os
from datetime import datetime, timedelta

# Import services for data collection
# Use absolute imports since backend is in sys.path
try:
    from services.weather import weather_service
    from services.satellite import satellite_service
except ImportError:
    # Fallback: add parent directory to path
    import sys
    backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if backend_path not in sys.path:
        sys.path.insert(0, backend_path)
    from services.weather import weather_service
    from services.satellite import satellite_service

# Define constants for Mysuru region
MYSURU_LAT = 12.2958
MYSURU_LON = 76.6394
MYSURU_REGION_RADIUS_KM = 150  # Approximate radius of Mysuru region in km

# Define optimal ranges for different crops
CROP_OPTIMAL_RANGES = {
    "ragi": {
        "rainfall_mm": (500, 900),
        "temperature_c": (20, 30),
        "nitrogen_kg_ha": (80, 120),
        "phosphorus_kg_ha": (40, 60),
        "potassium_kg_ha": (60, 80),
        "ndvi": (0.6, 0.8)
    },
    "maize": {
        "rainfall_mm": (700, 1100),
        "temperature_c": (22, 28),
        "nitrogen_kg_ha": (120, 160),
        "phosphorus_kg_ha": (60, 80),
        "potassium_kg_ha": (80, 100),
        "ndvi": (0.65, 0.85)
    },
    "sugarcane": {
        "rainfall_mm": (1000, 1500),
        "temperature_c": (24, 30),
        "nitrogen_kg_ha": (150, 200),
        "phosphorus_kg_ha": (60, 90),
        "potassium_kg_ha": (100, 150),
        "ndvi": (0.7, 0.9)
    },
    "paddy": {
        "rainfall_mm": (1000, 1600),
        "temperature_c": (22, 32),
        "nitrogen_kg_ha": (100, 140),
        "phosphorus_kg_ha": (50, 70),
        "potassium_kg_ha": (80, 120),
        "ndvi": (0.7, 0.85)
    }
}

# Define soil type characteristics
SOIL_TYPE_CHARACTERISTICS = {
    "red_sandy_loam": {
        "water_holding": "medium",
        "drainage": "good",
        "fertility": "medium",
        "suitable_crops": ["ragi", "maize"]
    },
    "black_cotton": {
        "water_holding": "high",
        "drainage": "poor",
        "fertility": "high",
        "suitable_crops": ["sugarcane", "paddy"]
    },
    "laterite": {
        "water_holding": "low",
        "drainage": "excellent",
        "fertility": "low",
        "suitable_crops": ["ragi"]
    },
    "clay": {
        "water_holding": "high",
        "drainage": "poor",
        "fertility": "medium",
        "suitable_crops": ["paddy", "sugarcane"]
    }
}


class DataProcessor:
    def __init__(self):
        self.weather_service = weather_service
        self.satellite_service = satellite_service
        self.data_cache_dir = Path(__file__).parent / "data_cache"
        self.data_cache_dir.mkdir(exist_ok=True)
    
    def get_weather_data(self, lat: float, lon: float) -> Dict[str, Any]:
        """
        Get current weather and forecast data for the given location
        """
        try:
            current_weather = self.weather_service.get_current_weather(lat, lon)
            forecast = self.weather_service.get_forecast(lat, lon)
            
            # Calculate average temperature and total rainfall from forecast
            forecast_list = forecast.get("forecast", [])
            if forecast_list:
                temps = [day.get("temperature", current_weather.get("temperature", 25.0)) for day in forecast_list]
                rainfall = sum([day.get("rain", 0) for day in forecast_list])
                avg_temp = sum(temps) / len(temps) if temps else current_weather.get("temperature", 25.0)
            else:
                avg_temp = current_weather.get("temperature", 25.0)
                rainfall = 0.0
            
            return {
                "current_temp": current_weather.get("temperature", 25.0),
                "current_humidity": current_weather.get("humidity", 70.0),
                "forecast_avg_temp": avg_temp,
                "forecast_rainfall_mm": rainfall
            }
        except Exception as e:
            print(f"Error getting weather data: {e}")
            # Return default values for Mysuru region
            return {
                "current_temp": 25.0,
                "current_humidity": 70.0,
                "forecast_avg_temp": 25.0,
                "forecast_rainfall_mm": 800.0  # Annual average in mm
            }
    
    def get_satellite_data(self, lat: float, lon: float, field_size_ha: float) -> Dict[str, Any]:
        """
        Get satellite data (NDVI, soil moisture) for the given location
        """
        try:
            ndvi_data = self.satellite_service.get_ndvi_data(lat, lon, field_size_ha)
            soil_moisture = self.satellite_service.get_soil_moisture(lat, lon, field_size_ha)
            crop_health = self.satellite_service.get_crop_health(lat, lon, field_size_ha)
            
            return {
                "ndvi": ndvi_data["ndvi_value"],
                "soil_moisture": soil_moisture["moisture_percentage"] / 100.0,  # Convert to 0-1 scale
                "crop_health": crop_health["health_percentage"] / 100.0  # Convert to 0-1 scale
            }
        except Exception as e:
            print(f"Error getting satellite data: {e}")
            # Return default values
            return {
                "ndvi": 0.7,
                "soil_moisture": 0.6,
                "crop_health": 0.7
            }
    
    def get_historical_climate_data(self, lat: float, lon: float) -> Dict[str, Any]:
        """
        Get historical climate data for the given location
        Returns accurate annual rainfall data based on location
        """
        # Define regional rainfall data for Karnataka (in mm)
        rainfall_data = {
            # Mysuru region (approx)
            (12.0, 12.5, 76.0, 77.0): 800,
            # Bangalore region (approx)
            (12.8, 13.2, 77.4, 77.8): 900,
            # Mandya region (approx)
            (12.4, 12.7, 76.7, 77.1): 750,
            # Hassan region (approx)
            (12.9, 13.2, 75.9, 76.3): 1050,
            # Chamarajanagar region (approx)
            (11.8, 12.2, 76.8, 77.2): 780,
            # Default for Karnataka
            (10.0, 18.0, 74.0, 79.0): 850
        }
        
        # Find the matching region based on coordinates
        annual_rainfall = 850  # Default value
        for (min_lat, max_lat, min_lon, max_lon), rainfall in rainfall_data.items():
            if min_lat <= lat <= max_lat and min_lon <= lon <= max_lon:
                annual_rainfall = rainfall
                break
        
        # Monthly average temperature in Celsius for Mysuru
        monthly_temp = {
            1: 22.5,  # January
            2: 24.5,  # February
            3: 27.0,  # March
            4: 28.0,  # April
            5: 27.5,  # May
            6: 25.0,  # June
            7: 24.0,  # July
            8: 24.0,  # August
            9: 24.5,  # September
            10: 24.0, # October
            11: 23.0, # November
            12: 22.0  # December
        }
        
        # Get current month
        current_month = datetime.now().month
        
        return {
            "annual_rainfall_mm": annual_rainfall,
            "monthly_rainfall_mm": 0,  # Will be calculated based on region in future update
            "avg_annual_temp_c": sum(monthly_temp.values()) / 12,
            "current_month_avg_temp_c": monthly_temp[current_month]
        }
    
    def process_soil_npk_data(self, n_value: float, p_value: float, k_value: float, 
                             soil_type: str) -> Dict[str, Any]:
        """
        Process soil NPK data and calculate soil fertility score
        """
        # Convert NPK values to kg/ha if they are in different units
        # Assuming the input values are already in kg/ha
        
        # Calculate soil fertility score based on NPK values and soil type
        # This is a simplified model
        
        # Base fertility scores for different soil types (0-1 scale)
        base_fertility = {
            "red_sandy_loam": 0.6,
            "black_cotton": 0.8,
            "laterite": 0.4,
            "clay": 0.7
        }
        
        # Optimal NPK ranges for general fertility
        optimal_n = (80, 200)  # kg/ha
        optimal_p = (40, 100)  # kg/ha
        optimal_k = (60, 150)  # kg/ha
        
        # Calculate NPK score (0-1 scale)
        n_score = min(1.0, max(0.0, (n_value - optimal_n[0]) / (optimal_n[1] - optimal_n[0])))
        p_score = min(1.0, max(0.0, (p_value - optimal_p[0]) / (optimal_p[1] - optimal_p[0])))
        k_score = min(1.0, max(0.0, (k_value - optimal_k[0]) / (optimal_k[1] - optimal_k[0])))
        
        # Combined NPK score with weights
        npk_score = 0.5 * n_score + 0.25 * p_score + 0.25 * k_score
        
        # Final fertility score combining base fertility and NPK score
        fertility_score = 0.4 * base_fertility.get(soil_type, 0.6) + 0.6 * npk_score
        
        return {
            "nitrogen_kg_ha": n_value,
            "phosphorus_kg_ha": p_value,
            "potassium_kg_ha": k_value,
            "soil_type": soil_type,
            "fertility_score": fertility_score,
            "npk_score": npk_score
        }
    
    def calculate_crop_suitability(self, crop: str, soil_data: Dict[str, Any], 
                                  weather_data: Dict[str, Any], 
                                  satellite_data: Dict[str, Any]) -> float:
        """
        Calculate crop suitability score (0-1) based on all data
        """
        if crop not in CROP_OPTIMAL_RANGES:
            return 0.0
        
        optimal = CROP_OPTIMAL_RANGES[crop]
        
        # Check if soil type is suitable for the crop
        soil_type = soil_data["soil_type"]
        soil_suitability = 1.0 if crop in SOIL_TYPE_CHARACTERISTICS.get(soil_type, {}).get("suitable_crops", []) else 0.5
        
        # Calculate rainfall suitability
        rainfall = weather_data["annual_rainfall_mm"]
        rainfall_min, rainfall_max = optimal["rainfall_mm"]
        if rainfall < rainfall_min:
            rainfall_suitability = max(0.3, rainfall / rainfall_min)
        elif rainfall > rainfall_max:
            rainfall_suitability = max(0.3, 1.0 - (rainfall - rainfall_max) / rainfall_max)
        else:
            rainfall_suitability = 1.0
        
        # Calculate temperature suitability
        temp = weather_data["avg_annual_temp_c"]
        temp_min, temp_max = optimal["temperature_c"]
        if temp < temp_min:
            temp_suitability = max(0.3, temp / temp_min)
        elif temp > temp_max:
            temp_suitability = max(0.3, 1.0 - (temp - temp_max) / temp_max)
        else:
            temp_suitability = 1.0
        
        # Calculate NPK suitability
        n_value = soil_data["nitrogen_kg_ha"]
        p_value = soil_data["phosphorus_kg_ha"]
        k_value = soil_data["potassium_kg_ha"]
        
        n_min, n_max = optimal["nitrogen_kg_ha"]
        p_min, p_max = optimal["phosphorus_kg_ha"]
        k_min, k_max = optimal["potassium_kg_ha"]
        
        n_suitability = 1.0 if n_min <= n_value <= n_max else max(0.5, 1.0 - abs(n_value - (n_min + n_max)/2) / (n_max - n_min))
        p_suitability = 1.0 if p_min <= p_value <= p_max else max(0.5, 1.0 - abs(p_value - (p_min + p_max)/2) / (p_max - p_min))
        k_suitability = 1.0 if k_min <= k_value <= k_max else max(0.5, 1.0 - abs(k_value - (k_min + k_max)/2) / (k_max - k_min))
        
        npk_suitability = (n_suitability + p_suitability + k_suitability) / 3
        
        # Calculate NDVI suitability
        ndvi = satellite_data["ndvi"]
        ndvi_min, ndvi_max = optimal["ndvi"]
        ndvi_suitability = 1.0 if ndvi_min <= ndvi <= ndvi_max else max(0.5, 1.0 - abs(ndvi - (ndvi_min + ndvi_max)/2) / (ndvi_max - ndvi_min))
        
        # Calculate overall suitability with weights
        overall_suitability = (
            0.2 * soil_suitability +
            0.2 * rainfall_suitability +
            0.15 * temp_suitability +
            0.25 * npk_suitability +
            0.2 * ndvi_suitability
        )
        
        return overall_suitability
    
    def prepare_prediction_data(self, crop: str, soil_type: str, n_value: float, 
                                     p_value: float, k_value: float, irrigation: str,
                                     lat: float = MYSURU_LAT, lon: float = MYSURU_LON, 
                                     field_size_ha: float = 1.0) -> Dict[str, Any]:
        """
        Prepare all data needed for crop yield prediction
        """
        # Get weather data
        weather_data = self.get_weather_data(lat, lon)
        
        # Get satellite data
        satellite_data = self.get_satellite_data(lat, lon, field_size_ha)
        
        # Get historical climate data
        climate_data = self.get_historical_climate_data(lat, lon)
        
        # Process soil NPK data
        soil_data = self.process_soil_npk_data(n_value, p_value, k_value, soil_type)
        
        # Combine all data
        combined_data = {
            "crop": crop,
            "soil_type": soil_type,
            "irrigation": irrigation,
            "field_size_ha": field_size_ha,
            "latitude": lat,
            "longitude": lon,
            "rainfall_mm": climate_data["annual_rainfall_mm"],
            "temperature_c": climate_data["avg_annual_temp_c"],
            "nitrogen_kg_ha": soil_data["nitrogen_kg_ha"],
            "phosphorus_kg_ha": soil_data["phosphorus_kg_ha"],
            "potassium_kg_ha": soil_data["potassium_kg_ha"],
            "ndvi": satellite_data["ndvi"],
            "soil_moisture": satellite_data["soil_moisture"],
            "crop_health": satellite_data.get("crop_health", 0.7)
        }
        
        # Calculate crop suitability
        suitability = self.calculate_crop_suitability(
            crop, soil_data, {**weather_data, **climate_data}, satellite_data
        )
        
        combined_data["crop_suitability"] = suitability
        
        return combined_data
    
    def prepare_feature_vector(self, data: Dict[str, Any], feature_names: List[str]) -> np.ndarray:
        """
        Prepare feature vector for model prediction based on feature names
        """
        # Create a DataFrame with one row
        df = pd.DataFrame([data])
        
        # One-hot encode categorical features
        df_encoded = pd.get_dummies(df, columns=["crop", "soil_type", "irrigation"], drop_first=False)
        
        # Ensure all required features are present
        for feature in feature_names:
            if feature not in df_encoded.columns:
                df_encoded[feature] = 0
        
        # Select only the features needed by the model
        X = df_encoded[feature_names].values
        
        return X