# kafka_producer.py
import json
import asyncio
from kafka.producer import KafkaProducer as BaseKafkaProducer
from kafka.errors import NoBrokersAvailable
from src.utils.config import Config
import time

class KafkaProducer:
    def __init__(self, bootstrap_servers, topic=Config.KAFKA_EMOJI_TOPIC, retry_attempts=3):
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.producer = None
        self.retry_attempts = retry_attempts
        self._connect()

    def _connect(self):
        """Connect to Kafka with retry logic"""
        for attempt in range(self.retry_attempts):
            try:
                self.producer = BaseKafkaProducer(
                    bootstrap_servers=self.bootstrap_servers,
                    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                    retries=3,
                    acks='all'
                )
                print(f"Successfully connected to Kafka at {self.bootstrap_servers}")
                return
            except NoBrokersAvailable:
                if attempt < self.retry_attempts - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    print(f"Kafka connection attempt {attempt + 1} failed. Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    print(f"Failed to connect to Kafka after {self.retry_attempts} attempts")
                    raise

    async def produce(self, data):
        """Asynchronously write data to Kafka"""
        if self.producer is None:
            raise Exception("Kafka producer not initialized")
        return await asyncio.get_event_loop().run_in_executor(None, self._produce, data)

    def _produce(self, data):
        """Synchronous Kafka producer method"""
        try:
            self.producer.send(self.topic, value=data)
            self.producer.flush(timeout=Config.KAFKA_PRODUCER_FLUSH_INTERVAL)
        except Exception as e:
            print(f"Error producing message: {e}")
            raise
