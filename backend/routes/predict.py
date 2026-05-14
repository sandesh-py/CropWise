from flask import Blueprint, request, jsonify
import numpy as np
from services.weather import weather_service
from services.satellite import satellite_service
from ml.models import MYSURU_CROPS, MYSURU_SOIL_TYPES
from ml.pipelines import ensemble_predict, PredictionInput, PredictionError

predict_bp = Blueprint('predict_bp', __name__)


@predict_bp.route('/crop', methods=['POST'])
def predict_crop():
    """Crop yield prediction using NPK, farm size, NDVI, and ML models.
    Request JSON: { 
        "N": number, "P": number, "K": number, "pH": number,
        "crop": str, "farmSize": number, "soilType": str, "irrigation": str,
        "latitude": float (optional), "longitude": float (optional)
    }
    Response JSON: { 
        "yield_per_hectare": number,
        "total_yield": number,
        "ndvi": number,
        "recommendations": [...],
        "weather": {...},
        "satellite_data": {...}
    }
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400

    try:
        # Extract required fields
        N = float(data.get('N', 0))
        P = float(data.get('P', 0))
        K = float(data.get('K', 0))
        pH = float(data.get('pH', 7.0))
        crop = data.get('crop', 'ragi')
        farm_size = float(data.get('farmSize', 1.0))  # in hectares
        soil_type = data.get('soilType', 'red_sandy_loam')
        irrigation = data.get('irrigation', 'rainfed')
        latitude = float(data.get('latitude', 12.2958))  # Default to Mysuru
        longitude = float(data.get('longitude', 76.6394))  # Default to Mysuru

        # Validate crop
        if crop not in MYSURU_CROPS:
            return jsonify({
                "error": f"Crop '{crop}' not supported. Supported crops: {MYSURU_CROPS}",
                "recommendations": [{"crop": c, "confidence": 0} for c in MYSURU_CROPS]
            }), 400

        # Validate soil type
        if soil_type not in MYSURU_SOIL_TYPES:
            soil_type = 'red_sandy_loam'  # Default fallback

        # Try to use ML pipeline for yield prediction
        try:
            prediction_input = PredictionInput(
                crop=crop,
                farmSize=farm_size,
                soilType=soil_type,
                nitrogen=N,
                phosphorus=P,
                potassium=K,
                irrigation=irrigation,
                latitude=latitude,
                longitude=longitude
            )
            
            # Get yield prediction from ML models
            ml_result = ensemble_predict(prediction_input)
            
            # Get weather data
            weather = weather_service.get_current_weather(city='Mysuru')
            
            return jsonify({
                "yield_per_hectare": ml_result.get("yield_per_hectare", 0),
                "total_yield": ml_result.get("total_yield", 0),
                "unit": ml_result.get("unit", "tons"),
                "ndvi": ml_result.get("satellite_data", {}).get("ndvi", 0.7),
                "crop": crop,
                "farm_size_hectares": farm_size,
                "soil_type": soil_type,
                "irrigation": irrigation,
                "weather": {
                    "temperature": weather.get('temperature', 25),
                    "humidity": weather.get('humidity', 65),
                    "description": weather.get('description', 'Clear')
                },
                "satellite_data": ml_result.get("satellite_data", {}),
                "crop_suitability": ml_result.get("crop_suitability", 0.5),
                "recommendations": ml_result.get("recommendations", []),
                "models": ml_result.get("models", {}),
                "shap_explanations": ml_result.get("shap_explanations", {}),
                "feature_importance": ml_result.get("feature_importance", {})
            })
            
        except PredictionError as e:
            return jsonify({"error": e.message}), e.status_code
        except Exception as ml_error:
            # Fallback to simple heuristic if ML fails
            print(f"ML prediction failed: {ml_error}, using fallback")
            return _fallback_prediction(N, P, K, pH, crop, farm_size, latitude, longitude)
            
    except ValueError as e:
        return jsonify({"error": f"Invalid input: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def _fallback_prediction(N, P, K, pH, crop, farm_size, lat, lon):
    """Fallback prediction using simple heuristics when ML models fail"""
    try:
        # Get weather
        weather = weather_service.get_current_weather(city='Mysuru')
        temp = float(weather.get('temperature', 25))
        humidity = float(weather.get('humidity', 65))
        
        # Get NDVI from satellite service
        try:
            ndvi_data = satellite_service.get_ndvi_data(lat=lat, lon=lon, field_size_ha=farm_size)
            ndvi = ndvi_data.get('ndvi_value', 0.7)
        except:
            ndvi = 0.7
        
        # Simple yield calculation based on crop, NPK, and NDVI
        base_yields = {
            'ragi': 2.5,
            'maize': 5.0,
            'sugarcane': 80.0,
            'paddy': 4.0
        }
        
        base_yield = base_yields.get(crop, 3.0)
        
        # Adjust for NPK (normalize around optimal)
        npk_factor = ((N/120) + (P/60) + (K/80)) / 3
        npk_factor = max(0.5, min(1.5, npk_factor))  # Clamp between 0.5 and 1.5
        
        # Adjust for NDVI
        ndvi_factor = 0.5 + (ndvi * 0.7)  # Scale NDVI to 0.5-1.2 range
        
        # Calculate yield per hectare
        yield_per_ha = base_yield * npk_factor * ndvi_factor
        total_yield = yield_per_ha * farm_size
        
        return jsonify({
            "yield_per_hectare": round(yield_per_ha, 2),
            "total_yield": round(total_yield, 2),
            "unit": "tons",
            "ndvi": round(ndvi, 3),
            "crop": crop,
            "farm_size_hectares": farm_size,
            "weather": {
                "temperature": temp,
                "humidity": humidity,
                "description": weather.get('description', 'Clear')
            },
            "satellite_data": {
                "ndvi": round(ndvi, 3),
                "soil_moisture": 0.6,
                "crop_health": 0.7
            },
            "crop_suitability": 0.7,
            "recommendations": [
                f"Base yield for {crop} is {base_yield} tons/ha",
                f"NPK levels are {'optimal' if 0.8 < npk_factor < 1.2 else 'suboptimal'}",
                f"NDVI index of {ndvi:.2f} indicates {'good' if ndvi > 0.7 else 'moderate'} crop health"
            ],
            "note": "Using fallback prediction method"
        })
    except Exception as e:
        return jsonify({"error": f"Fallback prediction failed: {str(e)}"}), 500


