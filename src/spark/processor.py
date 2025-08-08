import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import window, count, from_json, col, to_timestamp
from pyspark.sql.types import StructType, StructField, StringType, TimestampType
from src.utils.config import Config
import pyspark.sql.functions as F


class EmojiStreamProcessor:
    def __init__(self, kafka_bootstrap_servers, kafka_topic):
        """Initialize Spark Streaming session and configurations."""
        self.kafka_bootstrap_servers = kafka_bootstrap_servers
        self.kafka_topic = kafka_topic
        
        # Create checkpoint directory
        checkpoint_dir = os.path.join(os.getcwd(), "spark-checkpoint")
        os.makedirs(checkpoint_dir, exist_ok=True)
        
        # Initialize Spark Session with Windows-compatible configurations
        self.spark = (
            SparkSession
            .builder
            .appName("EmojiAnalytics")
            .config("spark.sql.streaming.checkpointLocation", checkpoint_dir)
            .config("spark.streaming.stopGracefullyOnShutdown", "true")
            .config("spark.hadoop.fs.defaultFS", "file:///")
            .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
            .config("spark.sql.adaptive.enabled", "false")
            .config("spark.sql.adaptive.coalescePartitions.enabled", "false")
            .getOrCreate()
        )

        # Set log level
        self.spark.sparkContext.setLogLevel("WARN")
        
        # Define schema for incoming emoji data
        self.schema = StructType([
            StructField("user_id", StringType(), True),
            StructField("emoji_type", StringType(), True),
            StructField("timestamp", StringType(), True),
            StructField("client_id", StringType(), True)  # Added missing field
        ])

    def create_streaming_query(self):
        """Create and return the streaming query."""
        # Convert bootstrap servers to string if it's a list
        bootstrap_servers = self.kafka_bootstrap_servers
        if isinstance(bootstrap_servers, list):
            bootstrap_servers = ",".join(bootstrap_servers)

        # Read from Kafka
        df = (self.spark
            .readStream
            .format("kafka")
            .option("kafka.bootstrap.servers", bootstrap_servers)
            .option("subscribe", self.kafka_topic)
            .option("startingOffsets", "latest")
            .option("failOnDataLoss", "false")
            .load())

        # Parse JSON data and handle timestamp conversion
        parsed_df = df.select(
            from_json(
                col("value").cast("string"),
                self.schema
            ).alias("parsed_data")
        ).select("parsed_data.*")

        # Convert string timestamp to timestamp type
        parsed_df = parsed_df.withColumn(
            "timestamp",
            to_timestamp(col("timestamp"))
        )

        # Add error handling for null timestamps
        parsed_df = parsed_df.filter(col("timestamp").isNotNull())

        # Process in windows with watermark
        windowed_counts = (
            parsed_df
            .withWatermark("timestamp", "30 seconds")
            .groupBy(
                window("timestamp", "15 seconds", "10 seconds"),
                "emoji_type"
            )
            .agg(count("*").alias("emoji_count"))
        )

        # Create Windows-compatible checkpoint location
        checkpoint_location = os.path.join(os.getcwd(), "checkpoint", "emoji-query")
        os.makedirs(checkpoint_location, exist_ok=True)

        # Write output to console with checkpointing
        query = windowed_counts \
            .writeStream \
            .outputMode("update") \
            .format("console") \
            .option("truncate", "false") \
            .option("checkpointLocation", checkpoint_location) \
            .trigger(processingTime="6 seconds") \
            .start()

        return query

    def process_stream(self):
        """Start processing the stream."""
        query = None
        try:
            print("Starting Spark Streaming...")
            query = self.create_streaming_query()
            print("Spark Streaming started successfully. Waiting for data...")
            query.awaitTermination()
        except Exception as e:
            print(f"Error in stream processing: {str(e)}")
            raise
        finally:
            if query:
                query.stop()
            self.spark.stop()

if __name__ == "__main__":
    # Use configuration from Config class
    processor = EmojiStreamProcessor(
        Config.KAFKA_BOOTSTRAP_SERVERS,
        Config.KAFKA_EMOJI_TOPIC
    )
    processor.process_stream()
