"""
Find the apps that are associated with a given Apigee product which have a particular custom flow var set.
"""
import os
from argparse import ArgumentParser

from custom_attribute_reporter.ApigeeApiHandler import ApigeeApiHandler
from custom_attribute_reporter.ApigeeApp import ApigeeApp

if __name__ == "__main__":
    parser = ArgumentParser(
        prog="Custom Attribute Query",
        description=__doc__
    )
    parser.add_argument('-e', '--apigee-organisation', choices=['nhsd-nonprod', 'nhsd-prod'], type=str,
                        required=True, help="The organisation to query (non-prod or prod).")
    parser.add_argument('-p', '--product-name', required=True, type=str,
                        help="The product whose apps you want to check for the given custom attribute.")
    parser.add_argument('-k', '--requested-flow-var-key', required=True, type=str,
                        help="The requested key to look for within the apim-app-flow-vars custom attribute.")
    args = parser.parse_args()
    access_token = os.getenv("APIGEE_ACCESS_TOKEN")

    if not access_token:
        raise EnvironmentError("The environment variable APIGEE_ACCESS_TOKEN must be set")

    apigee_api_handler = ApigeeApiHandler(args.apigee_organisation, access_token)
    associated_app_ids = apigee_api_handler.get_app_ids_for_product(args.product_name)
    apps_with_requested_flow_var: list[ApigeeApp] = []

    for app_id in associated_app_ids:
        custom_attr = apigee_api_handler.get_value_for_custom_flow_var(app_id, args.requested_flow_var_key)

        if not custom_attr:
            continue

        apps_with_requested_flow_var.append(ApigeeApp(id=app_id, requested_flow_vars=custom_attr))

    print(f"Total apps found with the requested flow var ({args.requested_flow_var_key}) = "
          f"{len(apps_with_requested_flow_var)}")

    for app in apps_with_requested_flow_var:
        print(str(app))
