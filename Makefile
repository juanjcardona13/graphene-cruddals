.PHONY: help
help:
	@echo "Please use \`make <target>' where <target> is one of"
	@grep -E '^\.PHONY: [a-zA-Z_-]+ .*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = "(: |##)"}; {printf "\033[36m%-30s\033[0m %s\n", $$2, $$3}'

.PHONY: dev-setup ## Install development dependencies
dev-setup:
	pip install -e ".[dev]"
	python -m pre_commit install

.PHONY: tests ## Run unit tests
tests:
	PYTHONPATH=. pytest tests --cov=graphene_cruddals -vv

.PHONY: format ## Format code
format:
	ruff format graphene_cruddals tests setup.py

.PHONY: lint ## Lint code
lint:
	ruff graphene_cruddals tests
