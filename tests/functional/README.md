# Functional Testing
​
Testing the API depending on mode of authentication.
​
This test suite uses [pytest](https://docs.pytest.org/en/stable/)
​
## Installing dependancies
​
* To install the project dependancies:
  * ```$ poetry install```
​
## Configuration through Environment Varibles
​
* To run the pytest script some environment variables must be set:
  - ```APPLICATION_RESTRICTED_SIGNING_KEY_PATH``` path to private key for signing the JWT.
  - ```APPLICATION_RESTRICTED_WITH_ASID_SIGNING_KEY_PATH``` path to private key for signing the JWT.
  - ```APPLICATION_RESTRICTED_API_KEY``` the API key for your application.
  - ```APPLICATION_RESTRICTED_WITH_ASID_API_KEY``` the API key for your application that contains an asid.
  - ```PDS_BASE_PATH``` The url for the applications Apigee proxy.
  - ```APIGEE_ENVIRONMENT``` The Apigee Environment you are working in.
  - ```KEY_ID``` The identifier for the key in the key store.
  - ```TEST_PATIENT_ID``` The NHS number of the test patient used for updates.
  - ```APIGEE_API_TOKEN``` An API token to be able to make calls to the Apigee API. It can be retrieved by running the `get_token()` [method](https://docs.apigee.com/api-platform/system-administration/using-gettoken).

​
## Run
​
* To run the pytest script:
  * ```$ poetry run pytest -v tests/functional/test_application_restricted.py```
