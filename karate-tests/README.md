# Karate tests for the PDS API

This repo contains the Karate tests for the PDS API. These are functional tests, with load test support as a sweet bonus.

## Pre-requisites

To run these tests, you'll need Java, Maven, and the standard personal-demographics-service-api environment variables.

### Java
You probably have Java installed as it's part of the main codebase build.

To avoid having to install a newer version of Java later when Karate demands it, you may want to install openjdk 17. This is what we run on CI too. It shouldn't break any of the existing `make` commands we have that use Java.

`sudo apt update sudo apt install openjdk-17-jdk`

### Maven

Maven is a build tool for Java. We use it to install dependencies and run the Karate tests. Live life to the max: treat yourself to the latest version!

1. Go to the directory where you want to install (unpack) maven. This may be a folder you use for other software too. It's not overly important - what's important is you tell your shell the path to the folder afterwards.
1. Download Maven. The latest version at the time of writing was: `wget https://dlcdn.apache.org/maven/maven-3/3.9.6/binaries/apache-maven-3.9.6-bin.tar.gz`
1. Unpack it. `tar xzvf apache-maven-3.9.6-bin.tar.gz`
1. Add the path to the `bin` folder of your `apache-maven-3.9.6` path to your PATH env variable
1. Reload the shell and verify Maven is on your path `mvn --version`


## Running the tests

All of the tests run against what's currently deployed on veit07.

### Functional tests 

To run the tests, make sure you are in the `karate-tests` folder.

Run all the functional tests in parallel:
    - `mvn test -Dtest=TestParallel`

There are also individual JUnit tests for running specific feature files. These may be more useful if you're developing / debugging tests and you only want to run certain scenarios.

Run all the tests in a given test file:
    - `mvn test -Dtest=HealthcareWorkerTests`

Run only one of the tests in a given test file:
    - `mvn test -Dtest=HealthcareWorkerTests#testGetPatient`

### Load tests
To see an example of how Karate can repurpose functional tests as a load test, we've got the `PatientsSimulation.scala` file, which lets us run the `getPatient.feature` file using Gatling:

Run the load tests:
    - `mvn clean test-compile gatling:test`

Woosh!