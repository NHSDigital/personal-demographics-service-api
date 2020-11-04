# Functional Testing
​
Testing the API depending on mode of authentication.
​
This test suite uses [pytest](https://docs.pytest.org/en/stable/)
​
## Setting up virtual env and installing dependancies
​
* To install the project dependancies:  
  * ```$ cd tests/functional```
  * ```$ pip install virtualenv```
  * ```$ virtualenv test_env```
  * ```$ source ./test_env/bin/activate```
  * ```$ pip install -r requirements.txt```
​
## Configuration through Environment Varibles
​
* To run the pytest script some environment variables must be set:
  - ```APPLICATION_RESTRICTED_SIGNING_KEY_PATH``` path to private key for signing the JWT.
  - ```APPLICATION_RESTRICTED_API_KEY``` the API key for your application.
  - ```PDS_BASE_PATH``` The url for the applications Apigee proxy.
  - ```APIGEE_ENVIRONMENT``` The Apigee Environment you are working in.
  - ```KEY_ID``` The identifier for the key in the key store.
​
## Run
​
* To run the pytest script:
  * ```$ pytest -v tests/functional/test_application_restricted.py```
