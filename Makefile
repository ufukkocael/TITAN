.PHONY: install start build stop clean test

install:
	pip install -e titan-core
	pip install -r requirements.txt

start:
	python start.py

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

test:
	pytest titan-core/tests/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf titan_memory/
