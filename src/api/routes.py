#!/usr/bin/env python3
import asyncio
from flask import Flask, request, jsonify, send_from_directory
import json
import logging
import os
from collections import deque, Counter
from datetime import datetime, timedelta
import time
from src.kafka_client.kafka_producer import KafkaProducer
from src.utils.config import Config

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Kafka producer (lazy initialization)
kafka_producer = None

# Emoji Statistics Tracking
class EmojiStatistics:
    def __init__(self, max_size=10):
        self.recent_emojis = deque(maxlen=max_size)  # Last 10 emojis
        self.total_count = 0
        self.session_start = datetime.now()
        
    def add_emoji(self, emoji_type, user_id, timestamp):
        """Add a new emoji and update statistics"""
        emoji_data = {
            'emoji_type': emoji_type,
            'user_id': user_id,
            'timestamp': timestamp,
            'datetime': datetime.now()
        }
        self.recent_emojis.append(emoji_data)
        self.total_count += 1
        
    def get_statistics(self):
        """Get current emoji statistics"""
        if not self.recent_emojis:
            return {
                'total_emojis': 0,
                'recent_count': 0,
                'top_emojis': [],
                'user_activity': [],
                'session_duration': 0,
                'avg_per_minute': 0,
                'recent_activity': []
            }
            
        # Count emoji types in recent emojis
        emoji_counts = Counter(item['emoji_type'] for item in self.recent_emojis)
        
        # Get top emojis with smart logic
        top_emojis_list = self._get_smart_top_emojis(emoji_counts)
        
        # Count user activity in recent emojis
        user_counts = Counter(item['user_id'] for item in self.recent_emojis)
        
        # Calculate session metrics
        session_duration = (datetime.now() - self.session_start).total_seconds() / 60  # minutes
        avg_per_minute = self.total_count / max(session_duration, 1)
        
        # Recent activity (last 5 emojis with timestamps)
        recent_activity = []
        for item in list(self.recent_emojis)[-5:]:
            recent_activity.append({
                'emoji': item['emoji_type'],
                'user': item['user_id'][:8] + '...' if len(item['user_id']) > 8 else item['user_id'],
                'time_ago': self._time_ago(item['datetime'])
            })
            
        return {
            'total_emojis': self.total_count,
            'recent_count': len(self.recent_emojis),
            'top_emojis': top_emojis_list,
            'user_activity': [{'user': user[:8] + '...' if len(user) > 8 else user, 'count': count} 
                            for user, count in user_counts.most_common(3)],
            'session_duration': round(session_duration, 1),
            'avg_per_minute': round(avg_per_minute, 2),
            'recent_activity': recent_activity
        }
        
    def _get_smart_top_emojis(self, emoji_counts):
        """Get top emojis with smart logic:
        - If multiple emojis have the same top count, show ALL of them
        - Otherwise, show top 3 emojis
        """
        if not emoji_counts:
            return []
            
        # Get all emoji counts sorted by count (descending)
        sorted_emojis = emoji_counts.most_common()
        
        if not sorted_emojis:
            return []
            
        # Get the highest count
        highest_count = sorted_emojis[0][1]
        
        # Find all emojis with the highest count
        top_count_emojis = [{'emoji': emoji, 'count': count} 
                           for emoji, count in sorted_emojis if count == highest_count]
        
        # If there are multiple emojis with the same top count, return all of them
        if len(top_count_emojis) > 1:
            return top_count_emojis
        
        # Otherwise, return top 3 emojis
        return [{'emoji': emoji, 'count': count} for emoji, count in sorted_emojis[:3]]
        
    def _time_ago(self, dt):
        """Calculate time ago string"""
        diff = datetime.now() - dt
        if diff.seconds < 60:
            return f"{diff.seconds}s ago"
        elif diff.seconds < 3600:
            return f"{diff.seconds // 60}m ago"
        else:
            return f"{diff.seconds // 3600}h ago"

# Global statistics instance
emoji_stats = EmojiStatistics()

def get_kafka_producer():
    global kafka_producer
    if kafka_producer is None:
        try:
            logger.info(f"🔗 Initializing Kafka producer with servers: {Config.KAFKA_BOOTSTRAP_SERVERS}")
            kafka_producer = KafkaProducer(
                bootstrap_servers=Config.KAFKA_BOOTSTRAP_SERVERS,
                topic=Config.KAFKA_EMOJI_TOPIC
            )
            logger.info("✅ Kafka producer initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Kafka producer: {e}")
            raise
    return kafka_producer

# CORS handler
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# Serve dashboard
@app.route('/')
def dashboard():
    """Serve the main dashboard"""
    return send_from_directory('.', 'dashboard.html')

@app.route('/dashboard.html')
def dashboard_html():
    """Serve the dashboard HTML file"""
    return send_from_directory('.', 'dashboard.html')

@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files"""
    return send_from_directory('.', filename)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Try to get Kafka producer to test connection
        producer = get_kafka_producer()
        kafka_status = "connected" if producer else "disconnected"
        
        response = jsonify({
            "status": "healthy",
            "service": "streammoji-api",
            "kafka_servers": Config.KAFKA_BOOTSTRAP_SERVERS,
            "kafka_topic": Config.KAFKA_EMOJI_TOPIC,
            "kafka_status": kafka_status,
            "environment": Config.ENVIRONMENT,
            "api_port": Config.API_PORT,
            "api_host": Config.API_HOST
        })
        
        return response, 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        response = jsonify({
            "status": "unhealthy",
            "service": "streammoji-api",
            "error": str(e),
            "kafka_servers": Config.KAFKA_BOOTSTRAP_SERVERS,
            "kafka_topic": Config.KAFKA_EMOJI_TOPIC,
            "environment": Config.ENVIRONMENT,
            "api_port": Config.API_PORT,
            "api_host": Config.API_HOST
        })
        
        return response, 500

@app.route('/statistics', methods=['GET'])
def get_statistics():
    """Get current emoji statistics"""
    try:
        current_stats = emoji_stats.get_statistics()
        return jsonify({
            "status": "success",
            "statistics": current_stats
        }), 200
    except Exception as e:
        logger.error(f"Error getting statistics: {str(e)}")
        return jsonify({"error": "Failed to get statistics"}), 500

@app.route('/emoji', methods=['POST', 'OPTIONS'])
def send_emoji():
    """Send emoji event to Kafka"""
    if request.method == 'OPTIONS':
        # Handle preflight request
        return jsonify({}), 200
    
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
        
        # Add to statistics tracking
        emoji_stats.add_emoji(
            emoji_type=data['emoji_type'],
            user_id=data['user_id'],
            timestamp=emoji_event['timestamp']
        )
        
        # Send to Kafka
        producer = get_kafka_producer()
        success = producer.send_message(emoji_event)
        
        if success:
            # Get current statistics
            current_stats = emoji_stats.get_statistics()
            
            logger.info(f"Emoji event sent successfully: {emoji_event}")
            response = jsonify({
                "status": "success",
                "message": "Emoji event sent to stream",
                "event": emoji_event,
                "statistics": current_stats
            })
            return response, 200
        else:
            logger.error("Failed to send emoji event to Kafka")
            response = jsonify({"error": "Failed to send emoji event"}), 500
            return response
            
    except Exception as e:
        logger.error(f"Error processing emoji event: {str(e)}")
        response = jsonify({"error": "Internal server error"}), 500
        return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

