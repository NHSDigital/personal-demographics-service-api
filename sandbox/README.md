# PDS FHIR API Sandbox

## The Why, What & How
### Why

The PDS FHIR API Sandbox environment is
* a tool through which a developer can understand the expected responses for a given scenario;
* a _starting point_ for stub server against which a developer can build an app;
* a place where future functionality can be demonstrated and understood better.

### What

The sandbox a is simple mock server produced through Karate, that returns, in most instances, predefined canned responses. 

It is stateless, so patients created or updated will not be persisted.

You should be able to find most predefined scenarios through either the [published specification](https://digital.nhs.uk/developer/api-catalogue/personal-demographics-service-fhir) or through the Postman collection maintain within this repo.

### How

To start the sandbox on your local machine, build and run the Dockerfile found in `sandbox`. As the application is created through Karate, the source code sits in an adjacent directory to `sandbox`, hence you need to run it from the top-level directory of the repository.
```
docker build -t nhs/pds-sandbox -f sandbox/Dockerfile . 
docker run --name karate-sandbox -p 9000:9000 nhs/pds-sandbox
```
Gotchas:
    * "Ubuntu WSL with Docker could not be found" If running in WSL2 ensure you have followed [these instructions](https://stackoverflow.com/questions/63497928/ubuntu-wsl-with-docker-could-not-be-found).
    * You may need to run it from root: prepend `sudo` to the above commands.
