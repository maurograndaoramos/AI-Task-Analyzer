.PHONY: setup run test docker-build docker-up docker-down clean

setup:
	@echo "Setting up development environment..."
	python3 -m venv venv
	. venv/bin/activate && pip install -r requirements.txt
	cp -n .env.example .env || true
	mkdir -p data logs

run:
	@echo "Starting development server..."
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	@echo "Running tests..."
	pytest

docker-build:
	@echo "Building Docker image..."
	docker-compose build

docker-up:
	@echo "Starting Docker containers..."
	docker-compose up -d

docker-down:
	@echo "Stopping Docker containers..."
	docker-compose down

clean:
	@echo "Cleaning up..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.log" -delete
