#!/usr/bin/env python3

import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from livekit import api
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# LiveKit configuration
LIVEKIT_URL = os.getenv("LIVEKIT_URL")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET")

if not all([LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET]):
    logger.error("Missing required LiveKit environment variables")
    exit(1)

@app.route('/getToken', methods=['GET'])
def get_token():
    try:
        # Get user name from query parameters
        name = request.args.get('name', 'Anonymous')
        
        # Generate a unique room name (you can customize this logic)
        room_name = f"support-room-{name.lower().replace(' ', '-')}"
        
        logger.info(f"Generating token for user: {name}, room: {room_name}")
        
        # Create access token
        token = api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET) \
            .with_identity(name) \
            .with_name(name) \
            .with_grants(api.VideoGrants(
                room_join=True,
                room=room_name,
                can_publish=True,
                can_subscribe=True,
            )).to_jwt()
        
        logger.info(f"Token generated successfully for {name}")
        return token, 200, {'Content-Type': 'text/plain'}
        
    except Exception as e:
        logger.error(f"Error generating token: {str(e)}")
        return jsonify({"error": "Failed to generate token"}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "livekit-token-server"}), 200

if __name__ == '__main__':
    logger.info("Starting LiveKit Token Server on port 5001...")
    logger.info(f"LiveKit URL: {LIVEKIT_URL}")
    app.run(host='0.0.0.0', port=5001, debug=False)
