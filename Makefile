.ONESHELL:
.PHONY: $(MAKECMDGOALS)
MAKEFLAGS += --no-print-directory
##
##  🚧 Wizaut developer tools
##
PACKAGE=wizaut
TAG=latest

help:           ## Show this help (default)
	@grep -Fh "##" $(MAKEFILE_LIST) | grep -Fv grep -F | sed -e 's/\\$$//' | sed -e 's/##//'

all:            ## Run an entire CI pipeline
	make format lint

format:         ## Format with all tools
	make black

lint:           ## Lint with all tools
	make ruff mypy

##

black:          ## Format with black
	black .

ruff:           ## Lint with ruff
	ruff check --fix .

mypy:           ## Lint with mypy
	mypy --no-incremental .

##

image:          ## Build Docker image
	docker build . -t ${PACKAGE}:${TAG}

##