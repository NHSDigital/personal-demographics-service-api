# Rate Limit testing

To ensure the proxy's rate limit has been configured correctly, there is a test suite, using Gatling, that runs a scenario multiple times, across multiple threads.

## Rate Limiting Apps

As part of the parameters passed in to the test, the name of the requesting app is required. These must match the app's name as defined in the karate-config.js file, eg rateLimitingApp.

## Single-app Testing

To test rate limit configuration of a given app or proxy run
```bash
mvn test-compile gatling:test -Dgatling.simulationClass=patients.GetPatientRateLimitSimulation -DrequestingApp=rateLimitingApp -DnumberOfRequests=41 -Dduration=60
```
where
* requestingApp - the name of the app, which ties to the environment names for its client id and secret
* numberOfRequests - the number of request you wish to send
* duration - the duration over which you wish to send the requests

The expected rate limit varies according to the environment, access mode, requests and requesting app. See karate-config.js  and the Simulation class for the variables the tests pick up.


## Two-app Testing

Some rate limits are counted per app, others are counted across all apps. In this way, one app's request can affect another.

To test rate limit configuration across two apps concurrently, run
Run the individual test:
```bash
mvn test-compile gatling:test -Dgatling.simulationClass=patients.GetPatientByTwoAppsSimulation -DrateLimitAppRequests=300 -DproxyRateLimitAppRequests=20 -Dduration=60
```