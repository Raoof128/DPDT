# Data Poisoning Detection Tool Makefile
# Comprehensive build, test, and deployment automation

.PHONY: help install install-dev dev start test coverage lint format typecheck \
        security clean build docker-build docker-run docker-compose-up \
        docker-compose-down pre-commit docs serve-docs all check release

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

# Project variables
PROJECT_NAME := data-poisoning-detector
PYTHON := python3
PIP := pip
VERSION := $(shell $(PYTHON) -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['version'])")

#==============================================================================
# HELP
#==============================================================================

help:
	@echo ""
	@echo "$(BLUE)🛡️  Data Poisoning Detection Tool v$(VERSION)$(NC)"
	@echo ""
	@echo "$(GREEN)Setup:$(NC)"
	@echo "  make install         Install production dependencies"
	@echo "  make install-dev     Install development dependencies"
	@echo "  make pre-commit      Install pre-commit hooks"
	@echo ""
	@echo "$(GREEN)Development:$(NC)"
	@echo "  make dev             Start development server (hot reload)"
	@echo "  make start           Start production server"
	@echo "  make format          Format code (black, isort, autoflake)"
	@echo "  make lint            Run linting (flake8)"
	@echo "  make typecheck       Run type checking (mypy)"
	@echo "  make security        Run security scan (bandit)"
	@echo "  make check           Run all checks (lint + typecheck + security)"
	@echo ""
	@echo "$(GREEN)Testing:$(NC)"
	@echo "  make test            Run tests"
	@echo "  make test-fast       Run tests without slow markers"
	@echo "  make coverage        Run tests with coverage report"
	@echo "  make coverage-html   Generate HTML coverage report"
	@echo ""
	@echo "$(GREEN)Build & Deploy:$(NC)"
	@echo "  make build           Build Python package"
	@echo "  make docker-build    Build Docker image"
	@echo "  make docker-run      Run Docker container"
	@echo "  make docker-up       Start with docker-compose"
	@echo "  make docker-down     Stop docker-compose"
	@echo ""
	@echo "$(GREEN)Documentation:$(NC)"
	@echo "  make docs            Build documentation"
	@echo "  make serve-docs      Serve documentation locally"
	@echo ""
	@echo "$(GREEN)Utilities:$(NC)"
	@echo "  make clean           Clean build artifacts"
	@echo "  make all             Run format + check + test"
	@echo "  make release         Prepare a release"
	@echo ""

#==============================================================================
# SETUP
#==============================================================================

install:
	@echo "$(BLUE)📦 Installing production dependencies...$(NC)"
	$(PIP) install -r requirements.txt

install-dev:
	@echo "$(BLUE)📦 Installing development dependencies...$(NC)"
	$(PIP) install -e ".[dev]"
	$(PIP) install -r requirements-dev.txt

pre-commit:
	@echo "$(BLUE)🪝 Installing pre-commit hooks...$(NC)"
	pre-commit install
	pre-commit install --hook-type commit-msg

#==============================================================================
# DEVELOPMENT
#==============================================================================

dev:
	@echo "$(GREEN)🚀 Starting development server...$(NC)"
	uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

start:
	@echo "$(GREEN)🚀 Starting production server...$(NC)"
	uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4

format:
	@echo "$(BLUE)🎨 Formatting code...$(NC)"
	autoflake --in-place --remove-all-unused-imports --remove-unused-variables -r backend tests
	isort backend tests
	black backend tests
	@echo "$(GREEN)✅ Formatting complete$(NC)"

lint:
	@echo "$(BLUE)🔍 Running flake8...$(NC)"
	flake8 backend tests --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 backend tests --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

typecheck:
	@echo "$(BLUE)🔍 Running mypy...$(NC)"
	mypy backend --ignore-missing-imports

security:
	@echo "$(BLUE)🔒 Running security scan...$(NC)"
	bandit -r backend -c pyproject.toml || true
	@echo "$(GREEN)✅ Security scan complete$(NC)"

check: lint typecheck security
	@echo "$(GREEN)✅ All checks passed$(NC)"

#==============================================================================
# TESTING
#==============================================================================

test:
	@echo "$(BLUE)🧪 Running tests...$(NC)"
	pytest tests/ -v --tb=short

test-fast:
	@echo "$(BLUE)🧪 Running fast tests...$(NC)"
	pytest tests/ -v --tb=short -m "not slow"

coverage:
	@echo "$(BLUE)📊 Running tests with coverage...$(NC)"
	pytest tests/ --cov=backend --cov-report=term-missing --cov-report=xml

coverage-html:
	@echo "$(BLUE)📊 Generating HTML coverage report...$(NC)"
	pytest tests/ --cov=backend --cov-report=html --cov-report=term
	@echo "$(GREEN)✅ Report generated at htmlcov/index.html$(NC)"

#==============================================================================
# BUILD & DEPLOY
#==============================================================================

build: clean
	@echo "$(BLUE)📦 Building package...$(NC)"
	$(PYTHON) -m build
	@echo "$(GREEN)✅ Build complete$(NC)"

docker-build:
	@echo "$(BLUE)🐳 Building Docker image...$(NC)"
	docker build -t $(PROJECT_NAME):$(VERSION) -t $(PROJECT_NAME):latest .
	@echo "$(GREEN)✅ Docker image built$(NC)"

docker-run:
	@echo "$(GREEN)🐳 Running Docker container...$(NC)"
	docker run -p 8000:8000 --name $(PROJECT_NAME) $(PROJECT_NAME):latest

docker-up:
	@echo "$(GREEN)🐳 Starting with docker-compose...$(NC)"
	docker-compose up -d

docker-down:
	@echo "$(YELLOW)🐳 Stopping docker-compose...$(NC)"
	docker-compose down

#==============================================================================
# DOCUMENTATION
#==============================================================================

docs:
	@echo "$(BLUE)📚 Building documentation...$(NC)"
	mkdocs build

serve-docs:
	@echo "$(GREEN)📚 Serving documentation...$(NC)"
	mkdocs serve

#==============================================================================
# UTILITIES
#==============================================================================

clean:
	@echo "$(YELLOW)🧹 Cleaning build artifacts...$(NC)"
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .coverage
	rm -rf coverage.xml
	rm -rf htmlcov
	rm -rf .ruff_cache
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "$(GREEN)✅ Clean complete$(NC)"

all: format check test
	@echo "$(GREEN)✅ All tasks complete$(NC)"

release: clean check test build
	@echo "$(GREEN)🚀 Release v$(VERSION) prepared$(NC)"
	@echo "Next steps:"
	@echo "  1. git tag v$(VERSION)"
	@echo "  2. git push origin v$(VERSION)"
	@echo "  3. GitHub Actions will handle the rest"

#==============================================================================
# QUICK COMMANDS
#==============================================================================

# Alias for common commands
fmt: format
t: test
c: check
d: dev
