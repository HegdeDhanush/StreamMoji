import os
import sys
import time

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

print(f"Current directory: {current_dir}")
print(f"Project root: {project_root}")
print(f"Python path: {sys.path[:3]}")

try:
    from pyspark.sql import SparkSession
    from pyspark.sql.functions import window, count, from_json, col, to_timestamp
    from pyspark.sql.types import StructType, StructField, StringType, TimestampType
    import pyspark.sql.functions as F
    print("✅ PySpark imports successful!")
except ImportError as e:
    print(f"❌ PySpark import error: {e}")
    print("Available packages:")
    import pkg_resources
    installed_packages = [d.project_name for d in pkg_resources.working_set]
    print([p for p in installed_packages if 'spark' in p.lower()])
    sys.exit(1)

# Import config with better error handling
try:
    from src.utils.config import Config
    print("✅ Config imported successfully!")
except ImportError as e:
    print(f"⚠️ Config import error: {e}")
    print("Using fallback configuration...")
    
    class Config:
        KAFKA_BOOTSTRAP_SERVERS = [os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')]
        KAFKA_EMOJI_TOPIC = os.getenv('KAFKA_EMOJI_TOPIC', 'emoji-events')

class EmojiStreamProcessor:
    def __init__(self, kafka_bootstrap_servers, kafka_topic):
        """Initialize Spark Streaming session and configurations."""
        self.kafka_bootstrap_servers = kafka_bootstrap_servers
        self.kafka_topic = kafka_topic
        
        # Create checkpoint directory
        if os.path.exists("/opt/spark/work-dir"):
            checkpoint_dir = "/opt/spark/work-dir/spark-checkpoint"
        else:
            checkpoint_dir = os.path.join(project_root, "spark-checkpoint")
        
        os.makedirs(checkpoint_dir, exist_ok=True)
        
        print("🚀 Initializing Spark Session...")
        print(f"Checkpoint directory: {checkpoint_dir}")
        
        # Initialize Spark Session
        builder = (
            SparkSession
            .builder
            .appName("EmojiAnalytics")
            .config("spark.sql.streaming.checkpointLocation", checkpoint_dir)
            .config("spark.streaming.stopGracefullyOnShutdown", "true")
            .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer")
            .config("spark.sql.adaptive.enabled", "false")
            .config("spark.sql.adaptive.coalescePartitions.enabled", "false")
            .config("spark.driver.memory", "1g")
            .config("spark.executor.memory", "1g")
            .config("spark.driver.maxResultSize", "512m")
            .config("spark.sql.execution.arrow.pyspark.enabled", "false")
            .config("spark.driver.host", "localhost")
            .config("spark.driver.bindAddress", "0.0.0.0")
            .config("spark.sql.streaming.forceDeleteTempCheckpointLocation", "true")
        )
        
        # Only add packages if not running with spark-submit
        if "spark-submit" not in " ".join(sys.argv):
            builder = builder.config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.1")
        
        # Set master if not already set
        try:
            self.spark = builder.getOrCreate()
        except Exception as e:
            print(f"Failed to create with default settings: {e}")
            print("Trying with local master...")
            builder = builder.master("local[2]")
            self.spark = builder.getOrCreate()
        
        # Set log level
        self.spark.sparkContext.setLogLevel("WARN")
        print("✅ Spark Session initialized successfully!")
        
        # Define schema for incoming emoji data
        self.schema = StructType([
            StructField("user_id", StringType(), True),
            StructField("emoji_type", StringType(), True),
            StructField("timestamp", StringType(), True),
            StructField("client_id", StringType(), True)
        ])

    def wait_for_kafka(self, max_retries=30):
        """Wait for Kafka to be available"""
        bootstrap_servers = self.kafka_bootstrap_servers
        if isinstance(bootstrap_servers, list):
            bootstrap_servers = ",".join(bootstrap_servers)
        
        print(f"🔍 Waiting for Kafka at {bootstrap_servers}...")
        
        # Simple socket check for Kafka
        import socket
        for attempt in range(max_retries):
            try:
                host, port = bootstrap_servers.split(':')
                port = int(port)
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex((host, port))
                sock.close()
                
                if result == 0:
                    print("✅ Kafka connection established!")
                    return True
                else:
                    print(f"Attempt {attempt + 1}/{max_retries}: Kafka not ready yet...")
                    time.sleep(2)
                    
            except Exception as e:
                print(f"Attempt {attempt + 1}/{max_retries}: Kafka check failed: {e}")
                time.sleep(2)
        
        print("❌ Failed to connect to Kafka after maximum retries")
        return False

    def create_streaming_query(self):
        """Create and return the streaming query."""
        bootstrap_servers = self.kafka_bootstrap_servers
        if isinstance(bootstrap_servers, list):
            bootstrap_servers = ",".join(bootstrap_servers)

        print(f"📡 Connecting to Kafka at: {bootstrap_servers}")
        print(f"📺 Subscribing to topic: {self.kafka_topic}")

        try:
            # Read from Kafka
            df = (self.spark
                .readStream
                .format("kafka")
                .option("kafka.bootstrap.servers", bootstrap_servers)
                .option("subscribe", self.kafka_topic)
                .option("startingOffsets", "latest")
                .option("failOnDataLoss", "false")
                .option("kafka.security.protocol", "PLAINTEXT")
                .option("maxOffsetsPerTrigger", 100)
                .load())

            # Parse JSON data
            parsed_df = df.select(
                from_json(
                    col("value").cast("string"),
                    self.schema
                ).alias("parsed_data")
            ).select("parsed_data.*")

            # Convert timestamp and filter nulls
            parsed_df = parsed_df.withColumn(
                "timestamp",
                to_timestamp(col("timestamp"))
            ).filter(col("timestamp").isNotNull())

            # Simple aggregation
            emoji_counts = (
                parsed_df
                .groupBy("emoji_type")
                .agg(count("*").alias("emoji_count"))
            )

            # Create checkpoint location
            if os.path.exists("/opt/spark/work-dir"):
                checkpoint_location = "/opt/spark/work-dir/checkpoint/emoji-query"
            else:
                checkpoint_location = os.path.join(project_root, "checkpoint", "emoji-query")
            
            os.makedirs(checkpoint_location, exist_ok=True)

            # Write output to console
            query = emoji_counts \
                .writeStream \
                .outputMode("update") \
                .format("console") \
                .option("truncate", "false") \
                .option("checkpointLocation", checkpoint_location) \
                .trigger(processingTime="10 seconds") \
                .start()

            return query

        except Exception as e:
            print(f"❌ Error creating streaming query: {str(e)}")
            import traceback
            traceback.print_exc()
            raise

    def process_stream(self):
        """Start processing the stream."""
        query = None
        try:
            # Wait for Kafka to be ready
            if not self.wait_for_kafka():
                raise Exception("Kafka is not available")
            
            print("🚀 Starting Spark Streaming...")
            query = self.create_streaming_query()
            print("✅ Spark Streaming started successfully. Waiting for data...")
            print("📊 You can view Spark UI at http://localhost:4040 (if port is exposed)")
            
            # Keep the stream running
            query.awaitTermination()
            
        except KeyboardInterrupt:
            print("\n🛑 Received interrupt signal. Stopping Spark Streaming...")
        except Exception as e:
            print(f"❌ Error in stream processing: {str(e)}")
            import traceback
            traceback.print_exc()
        finally:
            if query:
                print("🔄 Stopping query...")
                try:
                    query.stop()
                except:
                    pass
            print("🔄 Stopping Spark session...")
            try:
                self.spark.stop()
            except:
                pass

if __name__ == "__main__":
    print("🚀 Starting Emoji Stream Processor...")
    print(f"Environment: {os.getenv('ENVIRONMENT', 'unknown')}")
    
    try:
        processor = EmojiStreamProcessor(
            Config.KAFKA_BOOTSTRAP_SERVERS,
            Config.KAFKA_EMOJI_TOPIC
        )
        processor.process_stream()
    except Exception as e:
        print(f"💥 Failed to start processor: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

