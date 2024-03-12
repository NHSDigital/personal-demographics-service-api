# Karate tests for the PDS API

This repo contains the Karate tests for the PDS API. These are functional tests, with load test support in some cases, and mock servers in play in other cases.

Run all the functional tests in parallel:
    - `mvn test -Dtest=TestParallel`

Run the load tests:
    - `mvn clean test-compile gatling:test`
    
Run a mock using the standalone karate.jar. From the `src/test/java` folder:
    - `java -cp karate-1.4.1.jar:. com.intuit.karate.Main -m patients/patient-mock.feature -p 8080`



## Generating and validating NHS Numbers

There is an [online tool](https://data-gorilla.uk/en/healthcare/nhs-number/) for generating NHS numbers 

396 863 5779
706 526 1581
398 866 4804
444 601 0751
159 698 8371
291 277 4969
515 280 6657
577 501 2003
051 402 4194
240 874 5012

Do we really need validation for our mocks?!