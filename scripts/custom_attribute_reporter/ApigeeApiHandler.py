"""
Handler class for managing interactions with the Apigee API
"""
import http.client
import json
from typing import Union

from requests import HTTPError

from .ApigeeApiSession import ApigeeApiSession
from .ApigeeAppCustomAttributes import ApigeeAppCustomAttributes


class ApigeeApiHandler:
    APP_ENDPOINT = "apps"
    PRODUCT_ENDPOINT = "apiproducts"
    ATTRIBUTES_KEY = "attributes"
    APIM_FLOW_VARS_ATTR_NAME = "apim-app-flow-vars"
    RATE_LIMIT_ATTR_NAME = "ratelimiting"

    def __init__(self, apigee_org: str, auth_token: str):
        self._api_session = ApigeeApiSession(
            apigee_org,
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
            raise HTTPError(f'Something went wrong:\n{response.status_code}\n{response.text}')

        return response.json()

    def get_custom_attributes_for_app(
        self,
        app_id: str,
        requested_key_in_flow_vars: str,
        product_name: str
    ) -> ApigeeAppCustomAttributes:
        app_path = f"{self.APP_ENDPOINT}/{app_id}"
        response = self._api_session.get(app_path)

        if response.status_code != http.client.OK:
            raise HTTPError(f'Something went wrong for {app_path}:\n{response.status_code}\n{response.text}')

        attributes = response.json().get(self.ATTRIBUTES_KEY)
        apim_flow_var = self._find_apim_flow_var(attributes, requested_key_in_flow_vars)
        rate_limit = self._find_rate_limit(attributes, product_name)

        return ApigeeAppCustomAttributes(apim_flow_var, rate_limit)

    def _find_apim_flow_var(self, custom_attributes: dict, requested_key_in_flow_vars: str) -> Union[str, None]:
        apim_flow_var_attribute = next(
            (attribute for attribute in custom_attributes if attribute.get('name') == self.APIM_FLOW_VARS_ATTR_NAME),
            None
        )

        if not apim_flow_var_attribute:
            return None

        apim_flow_vars = json.loads(apim_flow_var_attribute.get('value'))
        return apim_flow_vars.get(requested_key_in_flow_vars)

    def _find_rate_limit(self, custom_attributes: dict, product_name: str) -> Union[str, None]:
        rate_limit_attribute = next(
            (attribute for attribute in custom_attributes if attribute.get('name') == self.RATE_LIMIT_ATTR_NAME),
            None
        )

        if not rate_limit_attribute:
            return None

        rate_limit = json.loads(rate_limit_attribute.get('value'))

        if product_name not in rate_limit.keys():
            return None

        return rate_limit[product_name]
