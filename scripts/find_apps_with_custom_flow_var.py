"""
Find the apps that are associated with a given Apigee product which have a particular custom flow var set or rate limit
set.
"""
import csv
import os
from argparse import ArgumentParser

from custom_attribute_reporter.ApigeeApiHandler import ApigeeApiHandler
from custom_attribute_reporter.ApigeeApp import ApigeeApp
from custom_attribute_reporter.CustomAttributesHandler import CustomAttributesHandler

OUTPUT_DIR = "scripts/custom_attribute_reporter/output"
OUTPUT_FILENAME = "apigee-app-custom-attribute-report.csv"
OUTPUT_FILE_HEADERS = ["app_id", "display_name", "url", "rate_limit", "requested_apim_flow_vars"]


def write_results_to_csv(matched_apigee_apps: list[ApigeeApp]) -> None:
    output_file = os.path.join(OUTPUT_DIR, OUTPUT_FILENAME)

    # Create the output directory if it does not exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(output_file, mode='w', newline='') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(OUTPUT_FILE_HEADERS)

        for app in matched_apigee_apps:
            csv_writer.writerow([app.id, app.name, app.url, app.rate_limit, app.requested_apim_flow_var])


if __name__ == "__main__":
    parser = ArgumentParser(
        prog="Custom Attribute Query",
        description=__doc__
    )
    parser.add_argument('-e', '--apigee-organisation', choices=['nhsd-nonprod', 'nhsd-prod'], type=str,
                        required=True, help="The organisation to query (non-prod or prod).")
    parser.add_argument('-p', '--product-name', required=True, type=str,
                        help="The product whose apps you want to check for certain custom attributes.")
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
        app_meta_data = apigee_api_handler.get_app_metadata(app_id)
        custom_attr_handler = CustomAttributesHandler(app_meta_data)
        rate_limit = custom_attr_handler.find_rate_limit_for_product(args.product_name)
        requested_flow_vars = custom_attr_handler.find_apim_flow_var(args.requested_flow_var_key)

        if not rate_limit and not requested_flow_vars:
            continue

        apps_with_requested_flow_var.append(ApigeeApp(
            app_id=app_id,
            name=app_meta_data.get("name"),
            rate_limit=rate_limit,
            requested_apim_flow_vars=requested_flow_vars,
            apigee_org=args.apigee_organisation,
        ))

    print(f"Total apps found with the requested flow var ({args.requested_flow_var_key}) or rate limits in place = "
          f"{len(apps_with_requested_flow_var)}")

    write_results_to_csv(apps_with_requested_flow_var)
    print(f"Contents written to: {OUTPUT_DIR}/{OUTPUT_FILENAME}")
