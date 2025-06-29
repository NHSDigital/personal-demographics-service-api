 We've got the `defaultTestAppRateLimitsSimulation.scala`, `rateLimitAppSimulation.scala`,`twoAppsRateLimitsSimulation.scala` files, which uses  `getPatientForDefaultApp.feature` and `getPatientForRateLimitingApp.feature` file using Gatling:

 These tests are designed to validate the rate-limiting functionality when an application is configured with app-specific rate limits. 

Run the individual test:
```bash
mvn test-compile gatling:test -Dgatling.simulationClass=patients.GetPatientByRateLimitAppSimulation -DrateLimitAppRequests=41 -Dduration=60

mvn test-compile gatling:test -Dgatling.simulationClass=patients.GetPatientByDefaultTestAppSimulation  -DproxyRateLimitAppRequests=31 -Dduration=60

mvn test-compile gatling:test -Dgatling.simulationClass=patients.GetPatientByTwoAppsSimulation -DrateLimitAppRequests=300 -DproxyRateLimitAppRequests=20 -Dduration=60
```