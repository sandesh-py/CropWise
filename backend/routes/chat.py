from flask import Blueprint, request, jsonify
from services.chat_service import chat_service

chat_bp = Blueprint('chat_bp', __name__)

@chat_bp.route('/', methods=['POST'])
def chat():
    """Handle chatbot requests"""
    data = request.get_json(silent=True)
    if not data or 'message' not in data:
        return jsonify({"error": "Message is required"}), 400
    
    try:
        message = data.get('message', '').strip()
        if not message:
            return jsonify({"error": "Message cannot be empty"}), 400
            
        response = chat_service.generate_response(message)
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500