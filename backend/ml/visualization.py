from typing import Dict, Any, List, Union
import numpy as np


def generate_visualization_data(data: Union[Dict[str, Any], Any], prediction_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate data for visualizations compatible with the new pipeline structure.
    
    Args:
        data: Either a PredictionInput dataclass or a dict with nitrogen, phosphorus, potassium fields
        prediction_result: Dictionary from ensemble_predict() containing models, final, etc.
    
    Returns:
        Dictionary with visualization data for charts
    """
    # Handle both dataclass and dict input
    if hasattr(data, 'nitrogen'):
        nitrogen = data.nitrogen
        phosphorus = data.phosphorus
        potassium = data.potassium
        crop = data.crop if hasattr(data, 'crop') else 'ragi'
    else:
        nitrogen = data.get('nitrogen', 0)
        phosphorus = data.get('phosphorus', 0)
        potassium = data.get('potassium', 0)
        crop = data.get('crop', 'ragi')
    
    # Get model predictions (new structure uses "models" key)
    models = prediction_result.get("models", {})
    final_prediction = prediction_result.get("final", prediction_result.get("yield_per_hectare", 0))
    
    return {
        "npk_chart": {
            "labels": ["Nitrogen", "Phosphorus", "Potassium"],
            "values": [nitrogen, phosphorus, potassium],
            "optimal_ranges": {
                "ragi": [100, 50, 70],
                "maize": [120, 60, 80],
                "paddy": [140, 70, 90],
                "sugarcane": [150, 60, 100]
            }
        },
        "yield_comparison": {
            "labels": ["LightGBM", "XGBoost", "CNN", "LSTM", "Random Forest", "Ensemble"],
            "values": [
                models.get("lightgbm", 0),
                models.get("xgboost", 0),
                models.get("cnn", 0),
                models.get("lstm", 0),
                models.get("random_forest", 0),
                final_prediction
            ]
        },
        "crop_suitability": {
            "value": prediction_result.get("crop_suitability", 0.5),
            "label": "Crop Suitability Score",
            "max": 1.0
        },
        "satellite_data": prediction_result.get("satellite_data", {
            "ndvi": 0.7,
            "soil_moisture": 0.6,
            "crop_health": 0.7
        })
    }