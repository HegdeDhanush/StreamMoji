#!/usr/bin/env python3
# src/utils/config.py

class Config:
    # API Settings
    API_HOST = "0.0.0.0"
    API_PORT = 5000
    
    # Kafka Settings
    KAFKA_BOOTSTRAP_SERVERS = ['localhost:9092']
    KAFKA_EMOJI_TOPIC = 'emoji-events'
    KAFKA_PRODUCER_FLUSH_INTERVAL = 0.5  # 500ms
    
    # Spark Settings
    SPARK_BATCH_INTERVAL = 2  # 2 seconds
    SPARK_APP_NAME = "EmojiAnalytics"
    
    # Scaling Settings
    MAX_CLIENTS_PER_SUBSCRIBER = 1000
    NUMBER_OF_CLUSTERS = 3
