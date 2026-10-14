PROFILE ?= quick
VENV := .venv
PYTHON := $(VENV)/bin/python

.PHONY: up install bench test lint api dashboard

up: ## Start PostgreSQL 17 and wait until it is healthy
	docker compose up -d --wait

install: ## Create the virtualenv and install the package with dev dependencies
	python3 -m venv $(VENV)
	$(PYTHON) -m pip install --upgrade pip
	$(PYTHON) -m pip install -e ".[dev]"

bench: ## Load, build and measure with PROFILE=quick|full
	$(PYTHON) benchmark.py all --profile $(PROFILE)

test: ## Run unit and integration tests
	$(PYTHON) -m pytest

lint: ## Check lint and formatting
	$(PYTHON) -m ruff check src tests
	$(PYTHON) -m ruff format --check src tests

api: ## Start the live-benchmark API server (port 8788) for the dashboard "Actualizar en vivo" button
	$(PYTHON) dashboard/api_server.py

dashboard: ## Start the React dashboard dev server (port 5173)
	cd dashboard && npm run dev
