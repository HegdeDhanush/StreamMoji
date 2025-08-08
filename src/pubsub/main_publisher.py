from kafka import KafkaProducer
import json
import threading
import time

class MainPublisher:
    def __init__(self, bootstrap_servers, input_topic, output_topics):
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        self.input_topic = input_topic
        self.output_topics = output_topics

    def distribute_message(self, message):
        # Route message to cluster publishers
        for topic in self.output_topics:
            self.producer.send(topic, message)
        self.producer.flush()

    def start_consuming(self):
        # Consume from input topic and distribute
        consumer = KafkaConsumer(
            self.input_topic,
            bootstrap_servers=self.producer.config['bootstrap.servers'],
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        
        for message in consumer:
            self.distribute_message(message.value)
