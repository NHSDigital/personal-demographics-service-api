# custom-attribute-reporter

## Purpose
This small application is used for retrieving apps associated with your Apigee API Product based on whether they have a
particular key within their `apim-app-flow-vars` custom attribute or product-specific rate limits in place.

This is useful for automating a process which would otherwise require manual overhead to search and view the custom
attributes of each associated application on the Apigee platform.

For a bit of additional context, the `apim-app-flow-vars` are a named custom attribute used by many APIM Producers. The
value is a JSON object containing keys/values which will affect the API behaviour for the given app. There is also
a `ratelimiting` custom attribute which may have rate limits set specifically for your product.

e.g. the apim-app-flow-vars may look something like this:
```{"pds": {"one-attribute": {"canDoSomething": "true"}, "another-attribute": {"canDoAnotherThing": "false"}}```

while the ratelimiting attribute value may look something like this:
```{"personal-demographics-internal-dev: {"quota": {"someRateLimitingParams": 100}}}```

In the PDS use case, we want to identify any apps that contain the `pds` key in this object or reference the relevant
PDS product for the requested environment in the rate limit custom attribute.

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

# Next, this method will retrieve app meta data including the app custom attributes
# You may want to iterate through the above list to find the meta data for all the relevant apps
app_meta_data = apigee_api_handler.get_app_metadata(app_id)
```

Then, to handle retrieving your required custom attribute data you will need to do the following
```python
# You will need to initialise a Custom Attributes Handler object
custom_attr_handler = CustomAttributesHandler(app_meta_data)

# This then exposes methods for retrieving the related rate limiting and apim-flow-var custom attributes
rate_limit = custom_attr_handler.find_rate_limit_for_product(product_name)
requested_flow_vars = custom_attr_handler.find_apim_flow_var(requested_flow_var_key)
```

It is up to you how you want to orchestrate the management of the application. In the case of the PDS FHIR API, we are
using Python's `ArgumentParser` to create a basic command line entrypoint in `find_apps_with_custom_flow_var.py`

## How to run in this repo (PDS)
- Ensure you have exported the APIGEE_ACCESS_TOKEN variable relevant to the Apigee organisation you want to query

```bash
# Either the below for non-prod
export SSO_LOGIN_URL=https://login.apigee.com
# Or for prod
export SSO_LOGIN_URL=https://nhs-digital-prod.login.apigee.com

# And finally
export APIGEE_ACCESS_TOKEN="$(get_token)"
```

- From the root directory run `poetry run python scripts/find_apps_with_custom_flow_var.py -e {ADD_YOUR_APIGEE_ENV} -p {ADD_YOUR_PRODUCT_NAME} -k {ADD_YOUR_FLOW_VAR_KEY}`
- e.g. `poetry run python scripts/find_apps_with_custom_flow_var.py -e nhsd-nonprod -p personal-demographics-internal-dev-application-restricted -k pds`
- This will output a CSV file to `scripts/custom_attribute_reporter/output` which will contain the information you need
