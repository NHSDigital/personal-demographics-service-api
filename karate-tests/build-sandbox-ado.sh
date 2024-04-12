#!/bin/bash
set -x -e
git clone https://github.com/karatelabs/karate.git karate
cd karate
git checkout c0597e5b7fcd61be47f916854e8473da11b37956
mvn clean install -P pre-release -pl -karate-robot,-karate-playwright,-karate-e2e-tests
cd karate-core
mvn package -P fatjar
cp target/karate-core-1.6.0-SNAPSHOT.jar /tmp/karate.jar
docker build -t nhs/pds-sandbox:latest .
docker run -d --name karate-sandbox nhs/pds-sandbox