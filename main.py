#!/usr/bin/env python3
from src.api.routes import app
from src.utils.config import Config

if __name__ == "__main__":
    app.run(
        host=Config.API_HOST,
        port=Config.API_PORT,
        debug=True
    )
