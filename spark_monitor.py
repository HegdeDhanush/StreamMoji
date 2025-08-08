import time
from pyspark.sql import SparkSession

class SparkMetricsMonitor:
    def __init__(self, spark_session):
        self.spark = spark_session
        
    def get_streaming_metrics(self):
        """Get current streaming metrics."""
        active_streams = self.spark.streams.active
        
        metrics = []
        for stream in active_streams:
            status = stream.status
            recent_progress = stream.recentProgress
            
            if recent_progress:
                latest = recent_progress[-1]
                metrics.append({
                    'name': status['name'],
                    'input_rate': latest.get('inputRate', 0),
                    'processing_rate': latest.get('processingRate', 0),
                    'batch_duration': latest.get('batchDuration', 0),
                    'num_input_rows': latest.get('numInputRows', 0),
                    'batch_id': latest.get('batchId', 0)
                })
                
        return metrics

    def print_metrics(self):
        """Print current metrics in a formatted way."""
        metrics = self.get_streaming_metrics()
        
        print("\n=== Streaming Metrics ===")
        for m in metrics:
            print(f"\nQuery: {m['name']}")
            print(f"Input Rate: {m['input_rate']:.2f} events/sec")
            print(f"Processing Rate: {m['processing_rate']:.2f} events/sec")
            print(f"Batch Duration: {m['batch_duration']} ms")
            print(f"Input Rows: {m['num_input_rows']}")
            print(f"Batch ID: {m['batch_id']}")

    def monitor_continuously(self, interval=5):
        """Monitor metrics continuously with specified interval."""
        try:
            while True:
                self.print_metrics()
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\nStopping metrics monitor...")

# Usage example
if __name__ == "__main__":
    # Get existing SparkSession
    spark = SparkSession.builder.getOrCreate()
    
    # Create and start monitor
    monitor = SparkMetricsMonitor(spark)
    monitor.monitor_continuously()
