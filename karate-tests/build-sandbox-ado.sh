#!/bin/bash
set -x -e
echo $KARATE_JARFILE_URL > /tmp/karate_jarfile_url
docker build -t nhs/pds-sandbox:latest --secret id=jarfile_url,src=/tmp/karate_jarfile_url .