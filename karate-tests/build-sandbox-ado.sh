#!/bin/bash
set -x -e
docker build -t nhs/pds-sandbox:latest .
docker run -d --name karate-sandbox nhs/pds-sandbox