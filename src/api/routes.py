#!/usr/bin/env python3
import asyncio
from flask import Flask, request, jsonify
from src.kafka.producer import KafkaProducer
from src.utils.config import Config
from asgiref.wsgi import WsgiToAsgi

app = Flask(__name__)

# Global variable to hold the producer
kafka_producer = None

def get_kafka_producer():
    """Lazy initialization of Kafka producer"""
    global kafka_producer
    if kafka_producer is None:
        try:
            kafka_producer = KafkaProducer(
                bootstrap_servers=Config.KAFKA_BOOTSTRAP_SERVERS,
                topic=Config.KAFKA_EMOJI_TOPIC
            )
        except Exception as e:
            print(f"Failed to initialize Kafka producer: {e}")
            return None
    return kafka_producer

@app.route('/emoji', methods=['POST'])
async def receive_emoji():
    try:
        data = request.json
        # Validate data structure
        if not all(key in data for key in ['user_id', 'emoji_type', 'timestamp']):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Get Kafka producer (lazy initialization)
        producer = get_kafka_producer()
        if producer is None:
            return jsonify({'error': 'Kafka service unavailable'}), 503
            
        # Write to Kafka producer asynchronously
        await producer.produce(data)
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        producer = get_kafka_producer()
        kafka_status = "connected" if producer else "disconnected"
        return jsonify({
            'status': 'healthy',
            'kafka': kafka_status
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

