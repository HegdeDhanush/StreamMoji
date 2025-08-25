# 🎯 StreamMoji - Real-Time Emoji Analytics Platform

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.3+-green.svg)](https://flask.palletsprojects.com/)
[![Apache Kafka](https://img.shields.io/badge/Apache%20Kafka-7.4+-red.svg)](https://kafka.apache.org/)
[![Apache Spark](https://img.shields.io/badge/Apache%20Spark-3.4+-orange.svg)](https://spark.apache.org/)
[![Docker](https://img.shields.io/badge/Docker-20.0+-blue.svg)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> A distributed, real-time emoji analytics platform built with microservices architecture, featuring live data streaming, intelligent analytics, and modern web dashboard.

*Where emojis meet real-time analytics!*

## 🚀 Features

### Real-Time Analytics
- **📊 Live Statistics**: Real-time tracking of emoji interactions with 5-second auto-refresh
- **🧠 Smart Top Emojis**: Intelligent algorithm showing all tied emojis or top 3 performers
- **📈 Session Metrics**: Duration tracking, rate per minute, and engagement analytics
- **🔄 Circular Buffer**: Efficient last-10-emojis tracking with optimal memory usage

### Modern Web Interface
- **🎨 Enhanced Dashboard**: Modern UI with CSS animations and responsive design
- **⚡ Individual Emoji Sending**: Randomized, timed emoji dispatch system
- **📝 Custom Emoji Forms**: Batch emoji creation with intelligent merging
- **📱 Mobile-Responsive**: Optimized for all device sizes

### Enterprise Architecture
- **🏗️ Microservices Design**: Decoupled Flask API, Kafka messaging, Spark processing
- **🐳 Docker Containerization**: Complete containerized deployment with fresh container creation
- **🔄 Event-Driven Architecture**: Scalable pub/sub messaging pattern
- **⚡ Stream Processing**: Real-time data processing with Apache Spark

## 🏗️ System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Dashboard │    │   Flask API     │    │   Apache Kafka  │
│   (Frontend)    │───▶│   (REST API)    │───▶│   (Message Bus) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
                                                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Data Storage  │◄───│  Spark Streaming│◄───│   Kafka Topic   │
│   (In-Memory)   │    │   (Processor)   │    │  (emoji-events) │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Component Overview

| Component | Technology | Purpose |
|-----------|------------|----------|
| **Frontend** | HTML5, CSS3, JavaScript | Interactive emoji dashboard with real-time updates |
| **API Layer** | Python Flask | REST endpoints, business logic, statistics tracking |
| **Message Queue** | Apache Kafka | Event streaming, message persistence, decoupling |
| **Stream Processor** | Apache Spark | Real-time analytics, aggregations, complex processing |
| **Infrastructure** | Docker Compose | Service orchestration, isolation, scaling |

## 📋 Prerequisites

Before running StreamMoji, ensure you have:

- **Docker Desktop** (v20.0+) - [Download here](https://www.docker.com/products/docker-desktop/)
- **Python 3.11+** (for local development) - [Download here](https://python.org/downloads/)
- **Java 8 or 11** (for Spark local runs) - [Download here](https://adoptium.net/)
- **PowerShell** (Windows) or **Bash** (Linux/Mac)

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/HegdeDhanush/StreamMoji.git
cd StreamMoji
```

### 2. Start the Platform (Fresh Containers)
```powershell
# Windows
.\start_2terminal.ps1

# Linux/Mac
./start_2terminal.sh
```

### 3. Access the Dashboard
- **Main Dashboard**: http://localhost:8082/dashboard.html
- **API Health**: http://localhost:5000/health
- **API Documentation**: http://localhost:5000/statistics

### 4. Start Sending Emojis! 🎉
- Click individual emoji buttons
- Use custom emoji forms for batch sending
- Watch real-time analytics update

## 🛠️ Development Setup

### Local Development
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate    # Windows

# Install dependencies
pip install -r requirements.txt

# Start development server
python main.py
```

### Docker Development
```bash
# Build and start all services
docker-compose -f docker-compose.working.yml up -d

# View logs
docker-compose -f docker-compose.working.yml logs -f

# Stop services
docker-compose -f docker-compose.working.yml down
```

## 📊 API Documentation

### Endpoints

#### Health Check
```http
GET /health
```
**Response:**
```json
{
  "status": "healthy",
  "service": "emoji-api",
  "kafka_servers": ["kafka:29092"],
  "kafka_status": "connected"
}
```

#### Send Emoji
```http
POST /emoji
Content-Type: application/json

{
  "user_id": "user123",
  "emoji_type": "fire"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Emoji event sent to stream",
  "statistics": {
    "total_emojis": 42,
    "recent_count": 8,
    "top_emojis": [
      {"emoji": "fire", "count": 15},
      {"emoji": "heart", "count": 12}
    ]
  }
}
```

#### Get Statistics
```http
GET /statistics
```

## 🧪 Testing

### Load Testing
```bash
# Simulate 5 concurrent users
python test_clients.py --num-clients 5 --server-url http://localhost:5000

# Custom load test
python test_clients.py --num-clients 10 --min-delay 0.5 --max-delay 2.0
```

### Container Validation
```powershell
# Check fresh container setup
.\test_fresh_containers.ps1
```

### Manual API Testing
```bash
# Test emoji submission
curl -X POST http://localhost:5000/emoji \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test_user","emoji_type":"fire"}'

# Get statistics
curl http://localhost:5000/statistics
```

## 📈 Analytics Features

### Smart Top Emojis Algorithm
- **Tie Detection**: When multiple emojis have the same top count, shows ALL tied emojis
- **Top N Display**: Otherwise displays top 3 performing emojis
- **Real-time Updates**: Statistics refresh every 5 seconds

### Metrics Tracked
- Total emoji count (lifetime)
- Recent activity (last 10 emojis)
- User engagement patterns
- Session duration and rate
- Top emoji rankings
- Real-time activity feed

## 🔧 Configuration

### Environment Variables
```bash
# Kafka Configuration
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_EMOJI_TOPIC=emoji-events

# API Configuration
API_HOST=0.0.0.0
API_PORT=5000

# Environment
ENVIRONMENT=development
```

### Docker Compose Services
- **Zookeeper**: Kafka coordination
- **Kafka**: Message streaming
- **Flask API**: Application server
- **Dashboard Server**: Frontend hosting

## 🏢 Production Deployment

### Scaling Considerations
```yaml
# docker-compose.production.yml
services:
  flask-api:
    deploy:
      replicas: 3
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M
```

### Monitoring
- Health check endpoints
- Container status monitoring
- Kafka topic monitoring
- Spark UI: http://localhost:4040

## 🔍 Troubleshooting

### Common Issues

**Docker not starting:**
```bash
# Check Docker daemon
docker ps

# Restart Docker Desktop
# On Windows: Restart Docker Desktop application
```

**Port conflicts:**
```bash
# Check port usage
netstat -an | findstr :5000
netstat -an | findstr :8082
netstat -an | findstr :9092
```

**Services not responding:**
```bash
# Check container logs
docker-compose -f docker-compose.working.yml logs flask-api
docker-compose -f docker-compose.working.yml logs kafka

# Restart with fresh containers
.\start_2terminal.ps1
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 for Python code
- Add tests for new features
- Update documentation for API changes
- Ensure Docker containers build successfully

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Apache Kafka** for reliable message streaming
- **Apache Spark** for powerful stream processing
- **Flask** for elegant web framework
- **Docker** for containerization platform
- Open source community for inspiration

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/HegdeDhanush/StreamMoji/issues)
- **Discussions**: [GitHub Discussions](https://github.com/HegdeDhanush/StreamMoji/discussions)
- **Documentation**: [Wiki](https://github.com/HegdeDhanush/StreamMoji/wiki)

---

**Built with ❤️ for real-time analytics and modern web experiences**

*StreamMoji - Where emojis meet big data! 🚀📊*
