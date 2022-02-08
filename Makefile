.PHONY: help
.DEFAULT_GOAL := help

filename = .

help:
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

install: ## Install requirements
	pip install -r requirements.txt

fmt format: ## Run code formatters
	isort $(filename)
	black $(filename)

lint: ## Run code linters
	isort --check $(filename)
	black --check $(filename)
	flake8 $(filename)
	mypy $(filename)
