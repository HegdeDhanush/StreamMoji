from kafka import KafkaProducer, KafkaConsumer
import json
import threading

class ClusterPublisher:
    def __init__(self, bootstrap_servers, input_topic, output_topic):
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        self.consumer = KafkaConsumer(
            input_topic,
            bootstrap_servers=bootstrap_servers,
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        self.input_topic = input_topic
        self.output_topic = output_topic

    def process_and_forward(self, message):
        # Optional: Add cluster-specific processing
        processed_message = self._process_message(message)
        self.producer.send(self.output_topic, processed_message)
        self.producer.flush()

    def _process_message(self, message):
        # Add any specific cluster processing logic
        return message

    def start(self):
        for message in self.consumer:
            self.process_and_forward(message.value)
