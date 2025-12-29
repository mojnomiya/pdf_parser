.PHONY: help install install-dev test lint format type-check clean build upload upload-test

help:  ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Install package
	pip install -e .

install-dev:  ## Install package with development dependencies
	pip install -e ".[dev]"
	pre-commit install

test:  ## Run tests
	pytest tests/ -v

test-cov:  ## Run tests with coverage
	pytest tests/ -v --cov=pdfparser --cov-report=html --cov-report=term

lint:  ## Run linting
	flake8 pdfparser/ tests/
	black --check pdfparser/ tests/

format:  ## Format code
	black pdfparser/ tests/
	isort pdfparser/ tests/

type-check:  ## Run type checking
	mypy pdfparser/

clean:  ## Clean build artifacts
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

build:  ## Build package
	python -m build

upload-test:  ## Upload to TestPyPI
	python -m twine upload --repository testpypi dist/*

upload:  ## Upload to PyPI
	python -m twine upload dist/*

check:  ## Run all checks (lint, type-check, test)
	$(MAKE) lint
	$(MAKE) type-check
	$(MAKE) test

release: clean build  ## Build and prepare for release
	@echo "Package built successfully. Run 'make upload-test' to upload to TestPyPI or 'make upload' for PyPI"