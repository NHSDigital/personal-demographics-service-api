#!/bin/bash
set -x -e
docker build -t nhs/pds-sandbox:latest .

# Check if the container exists
if docker container inspect karate-sandbox >/dev/null 2>&1; then
    # Check if the container is running
    if docker container inspect -f '{{.State.Running}}' karate-sandbox >/dev/null 2>&1; then
        # Stop the container
        docker container stop karate-sandbox >/dev/null
        docker wait karate-sandbox >/dev/null
    fi
    # Remove the container
    docker container rm karate-sandbox >/dev/null
fi