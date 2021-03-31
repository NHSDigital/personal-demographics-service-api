BASE :=-f docker-compose.yml

setup: build up

dev :
	docker build -t test_env .
	docker run -it --env-file docker.env -v $(PWD):/tests/ test_env /bin/bash

build :
	@echo "Building image..."
	docker-compose $(BASE) build

up :
	@echo "Starting up container..."
	docker-compose $(BASE) up -d

test-function :
	@echo "Executing BDD tests..."
	docker-compose $(BASE) run -T test_env pytest -m 