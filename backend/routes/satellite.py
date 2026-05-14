from flask import Blueprint, request, jsonify
from services.satellite import satellite_service
from extensions import cache
from loguru import logger

# Define a satellite blueprint directly for simpler registration
satellite_bp = Blueprint('satellite_bp', __name__)

@satellite_bp.route("/ndvi", methods=["GET", "POST"])
@cache.cached(timeout=3600, query_string=True)
def get_ndvi_data():
    """Get NDVI data from satellite imagery (supports GET with query params or POST with JSON)."""
    try:
        if request.method == "POST":
            data = request.get_json(silent=True) or {}
        else:
            data = request.args

        latitude = float(data.get("latitude", 12.2958))  # Default to Mysuru
        longitude = float(data.get("longitude", 76.6394))  # Default to Mysuru
        start_date = data.get("start_date")
        end_date = data.get("end_date")
        field_size_ha = float(data.get("field_size_ha")) if data.get("field_size_ha") else None

        logger.info(f"Fetching NDVI data for lat: {latitude}, lon: {longitude}")

        ndvi_data = satellite_service.get_ndvi_data(
            lat=latitude, 
            lon=longitude, 
            field_size_ha=field_size_ha,
            start_date=start_date, 
            end_date=end_date
        )
        return jsonify(ndvi_data)
    except Exception as e:
        logger.error(f"Failed to fetch NDVI data: {str(e)}")
        return jsonify({"error": str(e)}), 500


@satellite_bp.route("/soil-moisture", methods=["GET", "POST"])
@cache.cached(timeout=3600, query_string=True)
def get_soil_moisture():
    """Get soil moisture data from satellite imagery"""
    try:
        if request.method == "POST":
            data = request.get_json(silent=True) or {}
        else:
            data = request.args
        
        latitude = float(data.get("latitude", 12.2958))  # Default to Mysuru
        longitude = float(data.get("longitude", 76.6394))  # Default to Mysuru
        field_size_ha = float(data.get("field_size_ha")) if data.get("field_size_ha") else None
        
        logger.info(f"Fetching soil moisture data for lat: {latitude}, lon: {longitude}")

        moisture_data = satellite_service.get_soil_moisture(
            lat=latitude, 
            lon=longitude, 
            field_size_ha=field_size_ha
        )
        return jsonify(moisture_data)
    except Exception as e:
        logger.error(f"Failed to fetch soil moisture: {str(e)}")
        return jsonify({"error": str(e)}), 500


@satellite_bp.route("/land-cover", methods=["GET", "POST"])
@cache.cached(timeout=86400, query_string=True) # Cache for 24 hours
def get_land_cover():
    """Get land cover classification from satellite imagery"""
    try:
        if request.method == "POST":
            data = request.get_json(silent=True) or {}
        else:
            data = request.args
        
        latitude = float(data.get("latitude", 12.2958))  # Default to Mysuru
        longitude = float(data.get("longitude", 76.6394))  # Default to Mysuru
        
        logger.info(f"Fetching land cover data for lat: {latitude}, lon: {longitude}")

        land_cover_data = satellite_service.get_land_cover(
            lat=latitude, 
            lon=longitude
        )
        return jsonify(land_cover_data)
    except Exception as e:
        logger.error(f"Failed to fetch land cover: {str(e)}")
        return jsonify({"error": str(e)}), 500
