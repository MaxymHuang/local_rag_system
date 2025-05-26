# Makefile for Local RAG System

.PHONY: help install test test-unit test-integration test-all test-quick lint security clean coverage docker-test

# Default target
help:
	@echo "Local RAG System - Available Commands:"
	@echo ""
	@echo "Setup:"
	@echo "  install          Install all dependencies"
	@echo "  install-dev      Install development dependencies"
	@echo ""
	@echo "Testing:"
	@echo "  test             Run all tests"
	@echo "  test-unit        Run unit tests only"
	@echo "  test-integration Run integration tests only"
	@echo "  test-quick       Run quick unit tests"
	@echo "  coverage         Generate coverage report"
	@echo ""
	@echo "Quality:"
	@echo "  lint             Run code linting"
	@echo "  security         Run security scans"
	@echo "  format           Format code with black"
	@echo ""
	@echo "CI/CD:"
	@echo "  ci               Run full CI pipeline locally"
	@echo "  docker-test      Test Docker build"
	@echo ""
	@echo "Cleanup:"
	@echo "  clean            Clean up generated files"
	@echo "  clean-cache      Clean Python cache files"

# Installation
install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	pip install -r test_requirements.txt
	pip install flake8 black safety bandit

# Testing
test:
	python run_tests.py all

test-unit:
	python run_tests.py unit

test-integration:
	python run_tests.py integration

test-quick:
	python run_tests.py quick

coverage:
	pytest --cov=. --cov-report=term-missing --cov-report=html

# Quality checks
lint:
	python run_tests.py lint

security:
	python run_tests.py security

format:
	black . --line-length 127 --exclude="venv|.venv|__pycache__|.git"

# CI/CD
ci:
	python run_tests.py ci

docker-test:
	docker build -t local-rag-system .
	docker run --rm -d --name test-container -p 5000:5000 local-rag-system
	sleep 10
	curl -f http://localhost:5000/status || (docker stop test-container && exit 1)
	docker stop test-container

# Cleanup
clean:
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf coverage.xml
	rm -rf bandit-report.json
	rm -rf .pytest_cache/
	rm -rf dist/
	rm -rf build/
	rm -rf *.egg-info/

clean-cache:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

# Development helpers
dev-setup: install-dev
	@echo "Development environment setup complete!"
	@echo "Run 'make test' to verify everything works."

run-dev:
	python app.py

# Quick development workflow
dev: clean-cache lint test-quick
	@echo "Development checks passed!" 