#!/usr/bin/env python3
import asyncio
from flask import Flask, request, jsonify
from src.kafka.producer import KafkaProducer
from src.utils.config import Config
from asgiref.wsgi import WsgiToAsgi

app = Flask(__name__)
# Initialize Kafka producer
kafka_producer = KafkaProducer(
    bootstrap_servers=Config.KAFKA_BOOTSTRAP_SERVERS,
    topic=Config.KAFKA_EMOJI_TOPIC
)

@app.route('/emoji', methods=['POST'])
async def receive_emoji():
    try:
        data = request.json
        # Validate data structure
        if not all(key in data for key in ['user_id', 'emoji_type', 'timestamp']):
            return jsonify({'error': 'Missing required fields'}), 400
            
        # Write to Kafka producer asynchronously
        await kafka_producer.produce(data)
        return jsonify({'status': 'success'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

