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
* Once installed, run to add the apigee token to your environment variables:

```bash
export SSO_LOGIN_URL=https://login.apigee.com
export APIGEE_API_TOKEN="$(get_token -u $APIGEE_LOGIN)"
```


## Contributing



## Discussion






