#!/usr/bin/env python3
from src.api.routes import app
from src.utils.config import Config

if __name__ == "__main__":
    # Print configuration for debugging
    Config.print_config()
    
    print(f"🚀 Starting StreamMoji Flask API on {Config.API_HOST}:{Config.API_PORT}")
    print(f"🔗 Kafka Bootstrap Servers: {Config.KAFKA_BOOTSTRAP_SERVERS}")
    
    app.run(
        host=Config.API_HOST,
        port=Config.API_PORT,
        debug=True
    )
