# Karate tests for the PDS API

This repo contains the Karate tests for the PDS API. These are functional tests, with load test support as a sweet bonus.

## Karate documentation

If you're new to Karate, you would be well advised to get familiar with the excellent documentation that is available online. For this codebase in particular, the following resources are recommended:

- [Main Karate documentation](https://github.com/karatelabs/karate?tab=readme-ov-file#karate) - the one (big) pager that tells you virtually everything you need to know about how to write a Karate test
- [Karate JavaScript mocks documentation](https://github.com/karatelabs/karate/wiki/Karate-JavaScript-Mocks) - official docs about how to write Karate mocks using JavaScript
- [Karate Gatling documentation](https://github.com/karatelabs/karate/tree/develop/karate-gatling#karate-gatling) - official docs about setting up Karate-driven Gatling performance tests

StackOverflow is also a useful source of information - search using the `[Karate]` tag. And of course, online AI helpers can often help you find the answer you're looking for. They've read all the docs! 

## Pre-requisites

To run these tests, you'll need Java, Maven, and the standard personal-demographics-service-api environment variables.

### Java
You probably have Java installed as it's part of the main codebase build.

To avoid having to install a newer version of Java later when Karate demands it, you may want to install openjdk 17. This is what we run on CI too. It shouldn't break any of the existing `make` commands we have that use Java.

```bash
sudo apt update 
sudo apt install openjdk-17-jdk
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

## Important env variables

Typically we rely on the same env variables that were already defined in your .envrc file.

The newer variable you may not have defined is `INTERNAL_SERVER_BASE_URI` - ask for a value for this variable from someone with a working test build. Or, if in doubt, ask for their whole `.envrc` file...

## Developer productivity

- Karate:
    - You may want to install a VS Code extension to help with formatting, running tests etc. The free extension is [Karate Runner by Kirk Slota](https://marketplace.visualstudio.com/items?itemName=kirkslota.karate-runner)
- Java:
    - If you find yourself writing Java code, there are lots of options, a good one being [Language Support for Java by Red Hat](https://marketplace.visualstudio.com/items?itemName=redhat.java)
- JavaScript:
    - The Karate mocks are linted using eslint - you'll find the .eslintrc.json file in `src/test/java/mocks/sandbox`. [You can add an extension to help with linting in VSC](https://marketplace.visualstudio.com/items?itemName=dbaeumer.vscode-eslint) 

## Running the tests

All of the tests run against what's currently deployed on veit07.

### A note on test data

Because veit07 is a separate environment, test patients can be modified between automated test runs, and by other testers who use the environment. This means you'll need to be cautious in the way you write assertions.
There is also a limit of how many P9 patients exist, [consult this page before using a patient for a new type of request.](https://nhsd-confluence.digital.nhs.uk/display/DEMGRPH/NHS+Numbers+with+NHS+Login+for+FHIR+on+VEIT07)

### Functional tests 

To run the tests, make sure you are in the `karate-tests` folder.

Run all the functional tests in parallel:
```bash
mvn clean test -Dtest=TestParallel
```

If you want to run a subset of tests, at this point in time it seems easiest to modify one of the test profile files temporarily.

For example to run only the healthcare worker tests, change the path from "classpath:patients" to "classpath:patients/healthcareWorker"
Or add a tag to the tests you would like to run, and add it to the tag() method in the runner class.


### Load tests
To see an example of how Karate can repurpose functional tests as a load test, we've got the `PatientsSimulation.scala` file, which lets us run the `getPatient.feature` file using Gatling:

Run the load tests:
```bash
mvn clean test-compile gatling:test
```

## The sandbox (aka Karate mocks)

The sandbox is a fake FHIR API with functionality that allows us to use it in a few key scenarios:
1. As an API prototyping tool that allows us to rapidly build a working API that can illustrate new endpoint functionality.
1. As a versioning aid - different iterations of the sandbox and their related tests can be tagged to represent different versions of the API.
1. As documentation for the API. This was the sole use of the legacy sandbox. [Our public documentation page](https://digital.nhs.uk/developer/api-catalogue/personal-demographics-service-fhir) invites people to use the sandbox to explore some of our API functionality, and there is a collection of Postman requests to download too. The new Karate-based sandbox has been developed in a way so that the existing documentation and Postman collection are still valid.

### Running the sandbox locally as a separate process

If you want to run the sandbox locally to explore using Postman, for example, you can spin up an instance of the sandbox by using Java to run a Karate jarfile.

#### Option 1: Using Docker
We have a Dockerfile set up for the sandbox. You can build the image from this Dockerfile.

1. Build the image:
    ```bash
    cd karate-tests
    docker build -t nhs/pds-sandbox .
    ```
1. If you run the container you'll see the Karate mockserver logs
    ```bash
    docker run --name karate-sandbox -p 9090:9090 nhs/pds-sandbox 
    ```
1. Inspect the running container to discover its IP address:
    ```bash
    docker inspect <CONTAINER ID> | grep '"IPAddress":' | grep -oE '[0-9]+(\.[0-9]+){3}' | head -n 1
    ```
1. You should now be able to run the sandbox tests against this container to show things are working, e.g. :
    ```bash
    export APIGEE_ENVIRONMENT=docker && poetry run -vv pytest tests/sandbox/test_sandbox.py::TestSandboxRelatedPersonSuite
    ```

- If you want a shortcut to set the environment variable and run all tests, there is the make command:
    ```bash
    make test-karate-sandbox
    ```

#### Option 2: Building your own jarfile and running the sandbox locally
##### Building a jarfile
We're using JavaScript mocks on Windows, and there's a [known issue with sharing the port between WSL2 and Windows](https://stackoverflow.com/questions/78120386/why-cant-windows-make-requests-to-my-karate-mock-if-i-use-javascript-mocks), for which there is an unreleased fix (it will be included in the Karate 1.6 release). Because of this, for the time being we build our own jarfile from the latest Karate source (alternatively, ask a friend who's already built a jarfile you can use...).

The instructions for building a Karate jarfile from source [are all here](https://github.com/karatelabs/karate/wiki/Developer-Guide).

To make it easier to write the command for running the jarfile, you may well choose to create an environment variable that points to the jarfile, e.g.
```bash
export KARATE_JAR="/path/to/your/jarfile/karate-1.6.0-SNAPSHOT.jar"
```

##### Running the sandbox
To run the sandbox, go to your `src/test/java` folder and run the following command (in this command we have the `-p` switch to specify a port; if you omit this switch, a free port will be chosen at random, which may be what you want sometimes):
```bash
java -cp $KARATE_JAR:. com.intuit.karate.Main -m mocks/sandbox/sandbox.js -p 9090
```

You'll see output in your terminal to suggest the sandbox is running properly (or not). Again, you can test things by running the sandbox tests:  
  ```bash
  export APIGEE_ENVIRONMENT=karate && poetry run -vv pytest tests/sandbox/test_sandbox.py::TestSandboxRelatedPersonSuite
  ```

## CI Setup

As with other tests, the CI process takes place on both Github and Azure DevOps (ADO). 

- In the `Makefile`, a vital thing to note is how in the `release` operation we copy the `karate-tests` folder (`cp -R karate-tests dist`). This `release` step essentially builds the folder structure in ADO (via the `apigee-build.yml` script), so to be able to run the Karate tests it is vital to copy the `karate-tests` folder.
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

## Using Prism as a proxy to validate requests and responses against the OAS schema

Using the command-line tool Prism, we can set up a proxy server that validates all requests and responses against the rules laid down in our OAS file.

```bash
npm install -g @stoplight/prism-cli
```

Prism reads our JSON OAS spec directly and sets up listeners for each of the endpoints listed. Any responses that relate to these endpoints will be validated against the rules described in the OAS file. Note that we pass in two options when starting the Prism proxy:

- `--errors`: if there are any discrepancies between the described schema and the actual schema, Prism will return a 405 error with a description of the issue. This will cause our test to fail and the discrepancy will be visible in the test report.
- `--validate-request false`: a number of our tests intentionally send invalid requests - we're testing the API handles these errors correctly and we don't want Prism to raise errors. We do, however, want to make these requests and validate the response schemas. 

To start Prism with the desired config, execute the following command from the project root (not from the `karate-tests` folder).
To generate the JSON file, see that publish command in package.json 
```bash
prism proxy build/personal-demographics.json ${OAUTH_BASE_URI}/${PDS_BASE_PATH} --errors --validate-request false
```

There is a chance that we are testing endpoints that aren't yet covered by the OAS file. The `@no-oas` tag is used to identify scenarios that shouldn't run via the Prism proxy. The `TestSchemaParallel` test runner is configured to ignore these tests, and direct requests to the Prism proxy server. From the `karate-tests` folder, with Prism running in the background

```bash
mvn test -Dtest=TestSchemaParallel
```