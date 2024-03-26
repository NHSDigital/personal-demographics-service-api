# Karate tests for the PDS API

This repo contains the Karate tests for the PDS API. These are functional tests, with load test support as a sweet bonus.

## Pre-requisites

To run these tests, you'll need Java, Maven, and the standard personal-demographics-service-api environment variables.

### Java
You probably have Java installed as it's part of the main codebase build.

To avoid having to install a newer version of Java later when Karate demands it, you may want to install openjdk 17. This is what we run on CI too. It shouldn't break any of the existing `make` commands we have that use Java.

```bash
sudo apt update sudo apt install openjdk-17-jdk
```

### Maven

Maven is a build tool for Java. We use it to install dependencies and run the Karate tests. Live life to the max: treat yourself to the latest version!

1. Go to the directory where you want to install (unpack) maven. This may be a folder you use for other software too. It's not overly important - what's important is you tell your shell the path to the folder afterwards.
1. Download Maven. The latest version at the time of writing was: 
```bash
wget https://dlcdn.apache.org/maven/maven-3/3.9.6/binaries/apache-maven-3.9.6-bin.tar.gz
```
1. Unpack it. 
```bash
tar xzvf apache-maven-3.9.6-bin.tar.gz
```
1. Add the path to the `bin` folder of your `apache-maven-3.9.6` path to your PATH env variable
1. Reload the shell and verify Maven is on your path
```bash
mvn --version
```


## Running the tests

All of the tests run against what's currently deployed on veit07.

### Functional tests 

To run the tests, make sure you are in the `karate-tests` folder.

Run all the functional tests in parallel:
```bash
mvn test -Dtest=TestParallel
```

There are also individual JUnit tests for running specific feature files. These may be more useful if you're developing / debugging tests and you only want to run certain scenarios.

Run all the tests in a given test file:
```bash
mvn test -Dtest=HealthcareWorkerTests
```

Run only one of the tests in a given test file:
```
bash mvn test -Dtest=HealthcareWorkerTests#testGetPatient
```

### Load tests
To see an example of how Karate can repurpose functional tests as a load test, we've got the `PatientsSimulation.scala` file, which lets us run the `getPatient.feature` file using Gatling:

Run the load tests:
```bash
mvn clean test-compile gatling:test
```

## CI Setup

As with other tests, the CI process takes place on both Github and Azure DevOps (ADO). 

- In `.github/workflows/continuous-integration-workflow.yaml` you'll find the steps that are run on Github relating to installing Java and Maven.
- In the `Makefile`, a vital thing to note is how in the `release` operation we copy the `karate-tests` folder (`cp -R karate-tests dist`). This `release` step essentially builds the folder structure in ADO, so to be able to run the Karate tests it is vital to copy the `karate-tests` folder.
- In `azure/azure-pr-pipeline` you'll find the definition of the `karate-tests` stage that is run in ADO as part of the `build` pipeline. As with the other stages of the build, the `karate-tests` stage is in the `apigee_deployments` section:
```yaml
- environment: internal-dev
  stage_name: karate_tests
  post_deploy:
    - template: templates/pds-tests-karate.yml
  depends_on:
    - pytest_bdd_tests
```
- You can see that this section calls on the `pds-tests-karate.yml` template, which defines the actual steps that are run as part of the `karate-tests` stage.

### Test reporting in ADO

The `pds-tests-karate.yml` template runs the Karate tests and then publishes the results in two different ways:
1. The `PublishTestResults@2` task is called upon to read the JUnit XML results that were produced by the test run, and these results are published in the `Tests` tab of the build phase. More info on this ADO task [can be found here](https://learn.microsoft.com/en-us/azure/devops/pipelines/tasks/reference/publish-test-results-v2?view=azure-pipelines&tabs=trx%2Ctrxattachments%2Cyaml)
1. The `PublishBuildArtifacts@1` task is call upon to publish the Karate HTML reports that were produced by the test run. These results are available as downloadable build artifacts - you can download the whole folder as a zip file and then uncompress on your machine to view the results. More info on this ADO task [can be found here](https://learn.microsoft.com/en-us/azure/devops/pipelines/artifacts/build-artifacts?view=azure-devops&tabs=yaml)