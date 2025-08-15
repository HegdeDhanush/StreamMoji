#!/usr/bin/env python3
import asyncio
from flask import Flask, request, jsonify
import json
import logging
from src.kafka_client.kafka_producer import KafkaProducer  # Updated path
from src.utils.config import Config

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Kafka producer
kafka_producer = KafkaProducer(
    bootstrap_servers=Config.KAFKA_BOOTSTRAP_SERVERS,
    topic=Config.KAFKA_EMOJI_TOPIC
)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "emoji-api",
        "kafka_servers": Config.KAFKA_BOOTSTRAP_SERVERS,
        "kafka_topic": Config.KAFKA_EMOJI_TOPIC
    }), 200

@app.route('/emoji', methods=['POST'])
def send_emoji():
    """Send emoji event to Kafka"""
    try:
        # Get JSON data from request
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        # Validate required fields
        required_fields = ['user_id', 'emoji_type']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Add timestamp and client info
        import time
        import uuid
        
        emoji_event = {
            "user_id": data['user_id'],
            "emoji_type": data['emoji_type'],
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
            "client_id": str(uuid.uuid4())
        }
        
        # Send to Kafka
        success = kafka_producer.send_message(emoji_event)
        
        if success:
            logger.info(f"Emoji event sent successfully: {emoji_event}")
            return jsonify({
                "status": "success",
                "message": "Emoji event sent to stream",
                "event": emoji_event
            }), 200
        else:
            logger.error("Failed to send emoji event to Kafka")
            return jsonify({"error": "Failed to send emoji event"}), 500
            
    except Exception as e:
        logger.error(f"Error processing emoji event: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

