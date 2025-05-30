# custom-attribute-reporter

## Purpose
This small application is used for retrieving apps associated with your Apigee API Product based on whether they have a
particular key within their `apim-app-flow-vars` custom attribute or product-specific rate limits in place.

This is useful for automating a process which would otherwise require manual overhead to search and view the custom
attributes of each associated application on the Apigee platform.

For a bit of additional context, the `apim-app-flow-vars` are a named custom attribute used by many APIM Producers. The
value is a JSON object containing keys/values which will affect the API behaviour for the given app. While there is also
a `ratelimiting` custom attribute which may have rate limits set specifically for your product.

e.g. ```{"pds": {"one-attribute": {"canDoSomething": "true"}, "another-attribute": {"canDoAnotherThing": "false"}}```

In the PDS use case, we want to identify any apps that contain the `pds` key in this object.

## How to use
You will need to have the following values before using this app:
- Your Apigee API Product Name (in full) e.g. `personal-demographics-internal-dev`
- The Apigee organisation it resides in. Either `nhsd-nonprod` or `nhsd-prod`
- The key that you are looking for within the `apim-app-flow-vars` e.g. `pds`
- Your Apigee access token - it is easiest to retrieve this using the Apigee [get_token](https://docs.apigee.com/api-platform/system-administration/using-gettoken) utility

Note: your user that you authenticated with for your access token will need to be authorised for the Apigee organisation
you are interacting with.

```python
# You will need to initialise an Apigee Api Handler object
apigee_api_handler = ApigeeApiHandler({YOUR_APIGEE_ORG}, {YOUR_ACCESS_TOKEN})

# You can then call either of the methods it exposes
# Firstly, this retrieves the app IDs associated with your product
associated_app_ids = apigee_api_handler.get_app_ids_for_product({YOUR_PRODUCT_NAME})

# Finally, this method will retrieve the values of the ratelimiting and apim-app-flow var custom attributes
# You may want to iterate through the above list to find all the apps which have the requested key present
requested_custom_attributes = apigee_api_handler.get_custom_attributes_for_app(app_id, requested_flow_var_key)
```

It is up to you how you want to orchestrate the management of the application. In the case of the PDS FHIR API, we are
using Python's `ArgumentParser` to create a basic command line entrypoint in `find_apps_with_custom_flow_var.py`

## How to run in this repo
- Ensure you have exported the APIGEE_ACCESS_TOKEN variable

```bash
export SSO_LOGIN_URL=https://login.apigee.com
export APIGEE_ACCESS_TOKEN="$(get_token)"
```

- From the root directory run `poetry run python scripts/find_apps_with_custom_flow_var.py -e {ADD_YOUR_APIGEE_ENV} -p {ADD_YOUR_PRODUCT_NAME} -k {ADD_YOUR_FLOW_VAR_KEY}`
- e.g. `poetry run python scripts/find_apps_with_custom_flow_var.py -e nhsd-nonprod -p personal-demographics-internal-dev -k pds`
