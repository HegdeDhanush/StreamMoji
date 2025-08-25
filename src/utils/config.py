#!/usr/bin/env python3
# src/utils/config.py

import os
import sys

class Config:
    # API Settings
    API_HOST = os.getenv('API_HOST', '0.0.0.0')
    API_PORT = int(os.getenv('API_PORT', 5000))
    
    # Kafka Settings - supports both Docker and local
    KAFKA_BOOTSTRAP_SERVERS = [
        os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
    ]
    KAFKA_EMOJI_TOPIC = os.getenv('KAFKA_EMOJI_TOPIC', 'emoji-events')
    KAFKA_PRODUCER_FLUSH_INTERVAL = float(os.getenv('KAFKA_PRODUCER_FLUSH_INTERVAL', 0.5))
    
    # Spark Settings
    SPARK_BATCH_INTERVAL = int(os.getenv('SPARK_BATCH_INTERVAL', 2))
    SPARK_APP_NAME = os.getenv('SPARK_APP_NAME', 'EmojiAnalytics')
    
    # Scaling Settings
    MAX_CLIENTS_PER_SUBSCRIBER = int(os.getenv('MAX_CLIENTS_PER_SUBSCRIBER', 1000))
    NUMBER_OF_CLUSTERS = int(os.getenv('NUMBER_OF_CLUSTERS', 3))
    
    # Environment
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'local')
    
    @classmethod
    def get_kafka_servers_string(cls):
        """Return Kafka servers as comma-separated string for Spark"""
        return ','.join(cls.KAFKA_BOOTSTRAP_SERVERS)
    
    @classmethod
    def print_config(cls):
        """Print current configuration for debugging"""
        print("🔧 EmoStream Configuration:")
        print(f"   Environment: {cls.ENVIRONMENT}")
        print(f"   API Host: {cls.API_HOST}:{cls.API_PORT}")
        print(f"   Kafka Servers: {cls.KAFKA_BOOTSTRAP_SERVERS}")
        print(f"   Kafka Topic: {cls.KAFKA_EMOJI_TOPIC}")
        print(f"   Kafka Bootstrap Servers ENV: {os.getenv('KAFKA_BOOTSTRAP_SERVERS')}")
        print(f"   Current working directory: {os.getcwd()}")
        print(f"   Python path: {sys.path[:3]}...")  # Show first 3 paths
