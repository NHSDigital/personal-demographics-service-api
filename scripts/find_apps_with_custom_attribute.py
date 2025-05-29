"""
Find the value of a particular custom attribute on the apps that are associated with a given Apigee product.
"""
import os
from argparse import ArgumentParser

from custom_attribute_reporter.ApigeeApiHandler import ApigeeApiHandler


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

    for app_id in associated_app_ids:
        print(f"Checking {app_id}")
        print(apigee_api_handler.get_custom_attributes_for_app(app_id, args.requested_flow_var_key))
