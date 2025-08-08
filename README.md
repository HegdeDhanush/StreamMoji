# EmoStream: Real-Time Emoji Analytics Platform

## 📌 Overview

EmoStream is a real-time event-driven system designed to capture, process, and analyze emoji reactions during live sporting events. Built using Python, Flask, Apache Kafka, and Apache Spark Streaming, the platform demonstrates scalable real-time data ingestion, processing, and distribution architecture.

## 🔧 Tech Stack

* **API Layer**: Flask (REST API)
* **Messaging Backbone**: Apache Kafka
* **Streaming Engine**: Apache Spark Streaming
* **Simulation**: Python scripts (100+ concurrent clients)
* **Monitoring**: Spark metrics tracking
* **Testing**: PyTest

---

## 🧱 Architecture

```
[ Clients ]
    | POST /emoji
[ Flask API (main.py, routes.py) ]
    | → Kafka Producer
[ Kafka Topics: main, clusters, output ]
    | → Pub/Sub (main_pubsub.py, pubsub/)
    | → Spark Streaming (processor.py)
    | → Subscribers
```

---

## 📁 Project Structure

```
.
├── main.py                # Starts Flask API server
├── routes.py              # API routes
├── producer.py            # Kafka producer logic
├── consumer.py            # Kafka consumer logic
├── config.py              # Centralized configs
├── main_pubsub.py         # Starts pub-sub routing logic
├── src/
│   └── spark/
│       └── processor.py   # Spark Streaming processor
├── test_clients.py        # Simulates emoji event traffic
├── spark_monitor.py       # Monitors Spark metrics
├── tests/
│   └── cons_test.py       # Unit tests for consumers
```

---

## 🚀 Features

* Real-time emoji ingestion through REST API
* Kafka-based message distribution backbone
* Clustered pub-sub distribution logic
* Spark Streaming windowed aggregation (emoji counts)
* Simulated 100 concurrent clients
* Centralized config and component modularity
* Spark monitoring and system observability
* Unit tested components

---

## 🧪 How to Run

### 1. Start Flask API

```bash
python3 main.py
```

### 2. Start Pub/Sub System

```bash
python3 main_pubsub.py
```

### 3. Start Spark Streaming Job

```bash
spark-submit --master local[*] src/spark/processor.py
```

### 4. Simulate Clients

```bash
python3 test_clients.py --count 100 --duration 60
```

---

## 📊 Analytics Output (Example)

```json
{
  "window": "2025-08-08T15:00:00Z",
  "counts": {
    "😀": 42,
    "🔥": 18,
    "😡": 5
  }
}
```

---

## ⚙️ Configurable Parameters

Edit `config.py` to adjust:

* Kafka broker details
* Topic names
* Spark window durations
* Scaling parameters (clusters, clients)

---

## 📈 Monitoring

* Spark UI at `localhost:4040`
* Metrics include: processing time, throughput, lag
* `spark_monitor.py` logs key statistics

---

## ✅ Testing

```bash
pytest tests/
```

---

## 📌 Future Enhancements

* WebSocket client visualization dashboard
* Emoji sentiment analysis
* Cluster-based filtering and personalization
* AI-driven anomaly detection
* Horizontal scaling with Docker/K8s

---

## 🧑‍💻 Author

Built by Akash, Computer Science undergrad @ PES University (2022–2026).
