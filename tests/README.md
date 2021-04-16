# PDS Testing

Test suites to verify the PDS api.

* `scripts/` Cross-testing utilities
* `performance/` 
* `function/` BDD
* `user_restricted/` 
* `e2e/` 
* `sandbox/` Test sandbox api 

## Installation

* To be able to run tests that involve interacting with the apigee api (to CRUD apigee resources) you need an apigee api token.
* You will need to have the apigee commands to generate the token. You can install those commands use the `scripts/install_apigee_cmds.sh` file.
* Once installed, run the below to add the apigee token to your environment variables:

```bash
export SSO_LOGIN_URL=https://login.apigee.com
export APIGEE_API_TOKEN="$(get_token -u $APIGEE_LOGIN)"
```

### Install using Docker 

1. Install docker locally, please see here for more [details](https://docs.docker.com/get-docker/). 
2. In this folder run:

```bash
make dev
```

### Install Locally

* Please refer to the parent readme for more details.

### Environment Variables

* To run the pytest script some environment variables must be set:
  - ```APPLICATION_RESTRICTED_SIGNING_KEY_PATH``` path to private key for signing the JWT.
  - ```APPLICATION_RESTRICTED_WITH_ASID_SIGNING_KEY_PATH``` path to private key for signing the JWT.
  - ```APPLICATION_RESTRICTED_API_KEY``` the API key for your application.
  - ```APPLICATION_RESTRICTED_WITH_ASID_API_KEY``` the API key for your application that contains an asid.
  - ```PDS_BASE_PATH``` The url for the applications Apigee proxy.
  - ```APIGEE_ENVIRONMENT``` The Apigee Environment you are working in.
  - ```KEY_ID``` The identifier for the key in the key store.


## Pytest basics

* `quiet mode` --pytest -q
* `verbose mode` --pytest -v
* `run a specific test within a module` -- pytest test_mod.py::test_func
* `run a specific test within a class` -- pytest test_mod.py::TestClass::test_method
* `by test suite` -- pytest filename.py
* `keywords` -- pytest -k "KEYWORD" -k "KEYWORD_1 or KEYWORD_2" -k "KEYWORD_1 and KEYWORD_2"
* `marks` -- pytest -m MARK
* `stop after first failure` -- pytest -x
* `display print statements` -- pytest -s

## Contributing

Pytest will run any file which starts with `test_*.py` - test files should follow this convention. . 

### Marks

Marks allow you to tag a specific test. You can define tests in the `pytest.ini` file. You can run tests against specific marks:

```
pytest -m name_of_mark -v tests/
```

### Fixtures

Fixtures are the setup and teardown for our tests allowing us to arrange our tests. Pytest fixtures are defined in `conftest.py` files. Learn more [here](https://docs.pytest.org/en/stable/fixture.html) 