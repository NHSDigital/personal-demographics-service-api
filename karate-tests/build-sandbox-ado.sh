#!/bin/bash
set -x -e
docker build -t nhs/pds-sandbox:latest .

# Check if the container is running
if docker container inspect -f '{{.State.Running}}' karate-sandbox >/dev/null 2>&1; then
    # Stop the container
    docker container stop karate-sandbox >/dev/null
    # Remove the container
    docker container rm karate-sandbox >/dev/null
fi

# Run the container
docker run -d --name karate-sandbox -p 9090:9090 nhs/pds-sandbox:latest