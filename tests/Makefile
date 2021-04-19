BASE :=-f docker-compose.yml

setup: build up

dev :
	docker build -t test_env .
	docker run -it --env-file docker.env -v $(PWD):/tests/ test_env /bin/bash