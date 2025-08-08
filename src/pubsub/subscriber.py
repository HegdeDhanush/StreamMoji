from kafka import KafkaConsumer
import json
import threading

class Subscriber:
    def __init__(self, bootstrap_servers, topic, client_id):
        self.consumer = KafkaConsumer(
            topic,
            bootstrap_servers=bootstrap_servers,
            group_id=f'subscriber-group-{client_id}',
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        self.client_id = client_id
        self.is_active = True

    def receive_messages(self, callback=None):
        for message in self.consumer:
            if not self.is_active:
                break
            
            if callback:
                callback(message.value)
            else:
                print(f"Client {self.client_id} received: {message.value['emoji_type']}")

    def stop(self):
        self.is_active = False
        self.consumer.close()
