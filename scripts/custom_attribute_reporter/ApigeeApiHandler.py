"""
Handler class for managing
"""
import http.client
import json
from typing import Union

from .ApigeeApiSession import ApigeeApiSession


class ApigeeApiHandler:
    APP_ENDPOINT = "apps"
    PRODUCT_ENDPOINT = "apiproducts"
    ATTRIBUTES_KEY = "attributes"
    APIM_FLOW_VARS_ATTR_NAME = "apim-app-flow-vars"

    def __init__(self, apigee_org: str, auth_token: str):
        self._api_session = ApigeeApiSession(
            f"https://api.enterprise.apigee.com/v1/organizations/{apigee_org}/",
            auth_token
        )

    def get_app_ids_for_product(self, product_name: str) -> list[str]:
        product_path = f"{self.PRODUCT_ENDPOINT}/{product_name}"
        apps_query = {
            "query": "list",
            "entity": "apps"
        }

        response = self._api_session.get(product_path, params=apps_query)

        if response.status_code != http.client.OK:
            print(f'Something went wrong:\n {response.status_code}\n {response.text}')
            raise Exception

        return [app_id for app_id in response.json()]

    def get_custom_attributes_for_app(self, app_id: str, requested_key_in_flow_vars: str) -> Union[dict, None]:
        app_path = f"{self.APP_ENDPOINT}/{app_id}"
        response = self._api_session.get(app_path)

        if response.status_code != http.client.OK:
            raise Exception(f'Bad response for {app_path}:\n{response.status_code}\n{response.text}')

        attributes = response.json().get(self.ATTRIBUTES_KEY)

        if not attributes:
            raise Exception(f'No attributes for app {app_id}')

        for attribute in attributes:
            if attribute.get('name') != self.APIM_FLOW_VARS_ATTR_NAME:
                continue

            apim_app_flow_vars = json.loads(attribute.get('value'))

            if requested_key_in_flow_vars not in apim_app_flow_vars:
                continue

            return apim_app_flow_vars.get(requested_key_in_flow_vars)

        return None
