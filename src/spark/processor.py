from pyspark.sql import SparkSession
from pyspark.sql.functions import window, count, from_json, col, to_timestamp
from pyspark.sql.types import StructType, StructField, StringType, TimestampType
#from src.utils.config import Config
import pyspark.sql.functions as F


class EmojiStreamProcessor:
    def __init__(self, kafka_bootstrap_servers, kafka_topic):
        """Initialize Spark Streaming session and configurations."""
        self.kafka_bootstrap_servers = kafka_bootstrap_servers
        self.kafka_topic = kafka_topic
        
        # Initialize Spark Session with proper configurations
        '''self.spark = SparkSession \
            .builder \
            .appName("EmojiAnalytics") \
            .config("spark.streaming.stopGracefullyOnShutdown", "true") \
            .config("spark.sql.shuffle.partitions", "2") \
            .config("spark.hadoop.fs.defaultFS", "hdfs://localhost:9000") \
            .config("spark.streaming.kafka.maxRatePerPartition", "1000") \
            .config("spark.default.parallelism", "4") \
            .config("spark.streaming.backpressure.enabled", "true") \
            .getOrCreate()'''
            
        self.spark = (
    SparkSession
    .builder
    .appName("EmojiAnalytics")
    .config("spark.sql.streaming.checkpointLocation", "./spark-checkpoint")
    .config("spark.streaming.stopGracefullyOnShutdown", "true")
    .config("spark.hadoop.fs.defaultFS", "file:///")
    .getOrCreate()
)

        # Set log level
        self.spark.sparkContext.setLogLevel("WARN")
        
        # Define schema for incoming emoji data
        self.schema = StructType([
            StructField("user_id", StringType(), True),
            StructField("emoji_type", StringType(), True),
            StructField("timestamp", StringType(), True)  # Changed to StringType to match producer
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
        window("timestamp", "15 seconds", "10 seconds"),  # Larger windows
        "emoji_type"
    )
    .agg(count("*").alias("emoji_count"))
)



        # Apply aggregation logic with error handling
        aggregated_emojis = windowed_counts \
            .withColumn("aggregated_count", 
                       F.floor(col("emoji_count") / 10)) \
            .filter(col("aggregated_count") > 0) \
            .select(
                "window.start",
                "window.end",
                "emoji_type",
                "emoji_count",
                "aggregated_count"
            )

        # Write output to console with checkpointing
        query = aggregated_emojis \
            .writeStream \
            .outputMode("update") \
            .format("console") \
            .option("truncate", "false") \
            .option("checkpointLocation", "/tmp/checkpoint") \
            .trigger(processingTime="6 seconds") \
            .start()

        return query

    def process_stream(self):
        """Start processing the stream."""
        query = None
        try:
            query = self.create_streaming_query()
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
        ['localhost:9092'],
        'emoji-events'
    )
    processor.process_stream()
