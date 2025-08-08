# kafka_producer.py
import json
import asyncio
from kafka.producer import KafkaProducer as BaseKafkaProducer
from src.utils.config import Config

class KafkaProducer:
    def __init__(self, bootstrap_servers, topic=Config.KAFKA_EMOJI_TOPIC):
        self.producer = BaseKafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        self.topic = topic

    async def produce(self, data):
        # Asynchronously write data to Kafka
        return await asyncio.get_event_loop().run_in_executor(None, self._produce, data)

    def _produce(self, data):
        # Synchronous Kafka producer method
        self.producer.send(self.topic, value=data)
        self.producer.flush(timeout=Config.KAFKA_PRODUCER_FLUSH_INTERVAL)
