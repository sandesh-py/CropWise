from flask import Blueprint, request, jsonify
from services.weather import weather_service
from extensions import cache
from loguru import logger

weather_bp = Blueprint('weather_bp', __name__)

@weather_bp.route('/current', methods=['GET'])
@cache.cached(timeout=600, query_string=True)
def get_weather_current():
    """Alias for /api/weather/current — same as /api/weather"""
    logger.info("Fetching current weather via alias endpoint.")
    return get_weather_simple()


@weather_bp.route('/', methods=['GET'])
@cache.cached(timeout=600, query_string=True)
def get_weather_simple():
    """Simplified current weather endpoint: defaults to Mysuru and returns basic fields.
    Example: /api/weather?city=Mysuru
    """
    city = request.args.get('city', 'Mysuru')
    logger.info(f"Fetching simplified weather data for city: {city}")
    try:
        data = weather_service.get_current_weather(city=city)
        return jsonify({
            "city": data.get("location", {}).get("name", city),
            "temperature": data.get("temperature"),
            "humidity": data.get("humidity"),
            "description": data.get("description", ""),
            "wind_speed": data.get("wind_speed")
        })
    except Exception as e:
        logger.error(f"Failed to fetch weather for {city}: {str(e)}")
        return jsonify({"error": str(e)}), 500

@weather_bp.route('/forecast', methods=['GET'])
@cache.cached(timeout=3600, query_string=True)
def get_forecast():
    """Get weather forecast for a location. Defaults to Mysuru if lat/lon not provided."""
    lat = request.args.get('lat', type=float) or 12.2958  # Default to Mysuru
    lon = request.args.get('lon', type=float) or 76.6394  # Default to Mysuru
    days = request.args.get('days', default=7, type=int)
    
    logger.info(f"Fetching {days}-day forecast for lat: {lat}, lon: {lon}")
    try:
        forecast_data = weather_service.get_forecast(lat=lat, lon=lon, days=days)
        return jsonify(forecast_data)
    except Exception as e:
        logger.error(f"Failed to fetch forecast: {str(e)}")
        return jsonify({"error": str(e)}), 500
