import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, jsonify, request
from flask_cors import CORS
from loguru import logger
from flask_caching import Cache

# Configure Loguru
logger.remove()
logger.add(sys.stdout, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")
logger.add("logs/cropwise_{time:YYYY-MM-DD}.log", rotation="10 MB", retention="7 days", level="INFO")

from routes.chat import chat_bp
from routes.predict import predict_bp
from routes.weather import weather_bp
from routes.satellite import satellite_bp

app = Flask(__name__)
CORS(app)

from extensions import cache
cache.init_app(app, config={'CACHE_TYPE': 'SimpleCache', 'CACHE_DEFAULT_TIMEOUT': 300})

app.register_blueprint(chat_bp, url_prefix='/api/chat')
app.register_blueprint(predict_bp, url_prefix='/api/predict')
app.register_blueprint(weather_bp, url_prefix='/api/weather')
app.register_blueprint(satellite_bp, url_prefix='/api/satellite')

@app.before_request
def log_request_info():
    logger.info(f"Incoming {request.method} request to {request.path}")

@app.errorhandler(Exception)
def handle_exception(e):
    logger.exception(f"Unhandled exception occurred: {str(e)}")
    return jsonify({"error": "An internal server error occurred.", "details": str(e)}), 500

@app.route('/')
def index():
    logger.info("Health check endpoint hit")
    return jsonify({"message": "CropWise API is running with Enhanced Logging & Caching!"})

if __name__ == '__main__':
    logger.info("Starting CropWise Flask Server...")
    app.run(debug=True, port=8000)
