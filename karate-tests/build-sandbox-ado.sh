#!/bin/bash
set -x -e
wget "$KARATE_JARFILE_URL" > /tmp/karate.jar
docker build -t nhs/pds-sandbox:latest .
docker run -d --name karate-sandbox nhs/pds-sandbox