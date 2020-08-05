# Performance Testing

## Install dependancies

* To install the project dependancies:  
    * ```$ poetry install```

## Locust parameters

* To run the performance tests against a particular service or API the tests need some configuration.
* In order to run the tests it requires some values to run:
    * HOST: Which is the domain in which you intend to run against e.g. "https://nhsd-apim-testing.com"
    * Number of Users: Which is the amount of users you want to be running against the service
    * Hatch Rate: The amount of user created per second.

## Configuration through Environment Varibles

* To run the locust script some environment variables must be set to run the performance test aganst the service.
    * ``` CALLBACK_URL ``` the test app to use for authentication e.g. "https://nhsd-apim-testing.com"
    * ``` LOCUST_HOST ``` which is the domain in which the requests are fired to for example '{domain}/hello' e.g. "https://internal-dev.api.service.nhs.uk"
    * ``` CLIENT_ID ``` the API key used to identify the client during authentication.
    * ``` CLIENT_SECRET ``` the API secret used for client authorisation.
    * ``` BASE_PATH ``` the base path of the API e.g. "/personal-demographics"
    * ``` PATIENT_SEARCH ``` the api request parameters for e.g. 90000000001 or "?family=Jane" etc.

## Run

* To run the locust script:
    * ```$ locust -f ./tests/performance/locustfile.py```
    * The ``` -f ``` option is the path of the locust file 
    * This can be run with ```--headless``` to run within the CLI
