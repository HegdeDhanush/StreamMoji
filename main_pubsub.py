from src.pubsub.main_publisher import MainPublisher
from src.pubsub.cluster_publisher import ClusterPublisher
from src.pubsub.subscriber import Subscriber
import threading

def run_main_publisher():
    main_pub = MainPublisher(
        bootstrap_servers=['localhost:9092'],
        input_topic='emoji-events',
        output_topics=['cluster-1-topic', 'cluster-2-topic', 'cluster-3-topic']
    )
    main_pub.start_consuming()

def run_cluster_publisher(input_topic, output_topic):
    cluster_pub = ClusterPublisher(
        bootstrap_servers=['localhost:9092'],
        input_topic=input_topic,
        output_topic=output_topic
    )
    cluster_pub.start()

def run_subscriber(topic, client_id):
    subscriber = Subscriber(
        bootstrap_servers=['localhost:9092'],
        topic=topic,
        client_id=client_id
    )
    subscriber.receive_messages()

def main():
    # Start threads for different components
    threading.Thread(target=run_main_publisher).start()
    threading.Thread(target=run_cluster_publisher, args=('emoji-events', 'cluster-1-topic')).start()
    threading.Thread(target=run_cluster_publisher, args=('cluster-1-topic', 'client-output-topic')).start()
    
    # Create multiple subscribers
    for i in range(5):
        threading.Thread(target=run_subscriber, args=('client-output-topic', f'client-{i}')).start()

if __name__ == "__main__":
    main()
