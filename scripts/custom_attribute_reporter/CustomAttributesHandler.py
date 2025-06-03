import json
from typing import Union

from .ApigeeAppCustomAttribute import ApigeeAppCustomAttribute


class CustomAttributesHandler:
    CUSTOM_ATTRIBUTES_KEY = "attributes"
    APIM_FLOW_VARS_ATTR_NAME = "apim-app-flow-vars"
    RATE_LIMIT_ATTR_NAME = "ratelimiting"

    def __init__(self, app_meta_data: dict):
        self.custom_attributes = self._parse_custom_attributes(app_meta_data)

    def _parse_custom_attributes(self, app_meta_data: dict) -> list[ApigeeAppCustomAttribute]:
        custom_attributes: list[ApigeeAppCustomAttribute] = []

        for attribute in app_meta_data.get(self.CUSTOM_ATTRIBUTES_KEY):
            custom_attributes.append(
                ApigeeAppCustomAttribute(attribute.get("name"), attribute.get("value"))
            )

        return custom_attributes

    def get(self, custom_attr_name: str) -> Union[ApigeeAppCustomAttribute, None]:
        return next(
            (attribute for attribute in self.custom_attributes if attribute.name == custom_attr_name),
            None
        )

    def find_rate_limit_for_product(self, product_name: str) -> Union[dict, None]:
        rate_limit_custom_attr = self.get(self.RATE_LIMIT_ATTR_NAME)

        if not rate_limit_custom_attr:
            return None

        rate_limit_definition = json.loads(rate_limit_custom_attr.value)

        for key, value in rate_limit_definition.items():
            if product_name.startswith(key):
                return value

        return None

    def find_apim_flow_var(self, requested_key_in_flow_vars: str) -> Union[dict, None]:
        apim_flow_vars_custom_attr = self.get(self.APIM_FLOW_VARS_ATTR_NAME)

        if not apim_flow_vars_custom_attr:
            return None

        apim_flow_vars = json.loads(apim_flow_vars_custom_attr.value)

        return apim_flow_vars.get(requested_key_in_flow_vars)
