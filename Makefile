# EmoStream Makefile - Simplified Docker Commands

.PHONY: help start stop restart status logs clean build

# Default target
help:
	@echo "EmoStream Docker Commands:"
	@echo "  make start     - Start all services"
	@echo "  make stop      - Stop all services"
	@echo "  make restart   - Restart all services"
	@echo "  make status    - Show service status"
	@echo "  make logs      - Show logs from all services"
	@echo "  make clean     - Stop and remove all containers/volumes"
	@echo "  make build     - Build Docker images"
	@echo "  make test      - Run test clients"

# Start all services
start:
	@echo "Starting EmoStream services..."
	docker-compose up -d
	@echo "Services started! Check status with: make status"

# Stop all services
stop:
	@echo "Stopping EmoStream services..."
	docker-compose down

# Restart all services
restart: stop start

# Show service status
status:
	@echo "Service Status:"
	docker-compose ps

# Show logs
logs:
	docker-compose logs -f

# Clean everything
clean:
	@echo "Cleaning up all containers and volumes..."
	docker-compose down -v --remove-orphans
	docker system prune -f

# Build images
build:
	@echo "Building Docker images..."
	docker-compose build

# Run test clients
test:
	@echo "Running test clients..."
	python test_clients.py --count 10 --duration 30

# Quick start (build + start)
quick: build start
	@echo "EmoStream is ready! API available at http://localhost:5000"

