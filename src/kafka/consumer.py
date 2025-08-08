#!/usr/bin/env python3
import json
from kafka import KafkaConsumer
from typing import Dict, List
import logging
from datetime import datetime

class EmojiConsumer:
    def __init__(self, bootstrap_servers: str, topic: str):
        """
        Initialize the Kafka consumer for emoji processing
        
        Args:
            bootstrap_servers: Kafka bootstrap servers string (e.g. 'localhost:9092')
            topic: Kafka topic to consume from
        """
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.consumer = None
        self.setup_logging()
        
    def setup_logging(self):
        """Configure logging for the consumer"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def connect(self):
        """Establish connection to Kafka"""
        try:
            self.consumer = KafkaConsumer(
                self.topic,
                bootstrap_servers=self.bootstrap_servers,
                auto_offset_reset='latest',
                enable_auto_commit=True,
                group_id='emoji_consumer_group',
                value_deserializer=lambda x: json.loads(x.decode('utf-8'))
            )
            self.logger.info(f"Connected to Kafka topic: {self.topic}")
        except Exception as e:
            self.logger.error(f"Failed to connect to Kafka: {str(e)}")
            raise
    
    def process_message(self, message: Dict) -> None:
        """
        Process a single message from Kafka
        
        Args:
            message: Decoded Kafka message containing emoji data
        """
        try:
            # Extract message data
            user_id = message.value.get('user_id')
            emoji_type = message.value.get('emoji_type')
            timestamp = message.value.get('timestamp')
            
            # Log the received emoji
            self.logger.info(f"Received emoji: {emoji_type} from user: {user_id} at {timestamp}")
            
            # Here you can add additional processing logic
            # For example, storing in a database, updating metrics, etc.
            
        except Exception as e:
            self.logger.error(f"Error processing message: {str(e)}")
    
    def run(self):
        """Main consumer loop"""
        try:
            self.connect()
            self.logger.info("Starting to consume messages...")
            
            for message in self.consumer:
                self.process_message(message)
                
        except KeyboardInterrupt:
            self.logger.info("Shutting down consumer...")
        except Exception as e:
            self.logger.error(f"Unexpected error: {str(e)}")
        finally:
            if self.consumer:
                self.consumer.close()
                self.logger.info("Consumer closed")

def main():
    # Configuration
    KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"
    KAFKA_TOPIC = "emoji-topic"  # Make sure this matches your producer topic
    
    # Create and run consumer
    consumer = EmojiConsumer(KAFKA_BOOTSTRAP_SERVERS, KAFKA_TOPIC)
    consumer.run()

if __name__ == "__main__":
    main()
