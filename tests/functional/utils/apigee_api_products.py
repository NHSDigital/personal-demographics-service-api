from api_test_utils.apigee_api import ApigeeApi
from api_test_utils.api_session_client import APISessionClient
from . import helper
import logging

LOGGER = logging.getLogger(__name__)

class ApigeeApiProducts(ApigeeApi):
    """ A simple class to help facilitate CRUD operations for products in Apigee """

    def __init__(self, org_name: str = "nhsd-nonprod"):
        super().__init__(org_name)

        # Default product properties
        self.scopes = []
        self.api_resources = []
        self.environments = ["internal-dev"]
        self.access = "public"
        self.rate_limit = "10ps"
        self.proxies = []
        self.attributes = [
            {"name": "access", "value": self.access},
            {"name": "ratelimit", "value": self.rate_limit}
        ]
        self.quota = 500
        self.quota_interval = "1"
        self.quota_time_unit = "minute"

    def _product(self):
        return {
            "apiResources": self.api_resources,
            "approvalType": "auto",
            "attributes": self.attributes,
            "description": "",
            "displayName": self.name,
            "name": self.name,
            "environments": self.environments,
            "quota": self.quota,
            "quotaInterval": self.quota_interval,
            "quotaTimeUnit": self.quota_time_unit,
            "scopes": self.scopes,
            "proxies": self.proxies
        }

    def update_ratelimits(self, quota: int, quota_interval: str, quota_time_unit: str, rate_limit: str, api_products):
        """ Update the product set quota values """
        self.quota = quota
        self.quota_interval = quota_interval
        self.quota_time_unit = quota_time_unit
        self.rate_limit = rate_limit
        self.attributes[1]["value"] = rate_limit
        return self._update_product(api_products)

    def update_attributes(self, attributes: dict, api_products):
        """ Update the product attributes """
        updated_attributes = [
            {"name": "access", "value": self.access},
            {"name": "ratelimit", "value": self.rate_limit}
        ]
        for key, value in attributes.items():
            updated_attributes.append({"name": key, "value": value})
        self.attributes = updated_attributes
        return self._update_product(api_products)

    def update_environments(self, environments: list, api_products):
        """ Update the product environments """
        permitted_environments = ["internal-dev", "internal-dev-sandbox", "internal-qa", "internal-qa-sandbox", "ref"]
        if not set(environments) <= set(permitted_environments):
            raise RuntimeError(f"Failed updating environments! specified environments not permitted: {environments}"
                               f"\n Please specify valid environments: {permitted_environments}")
        self.environments = environments
        return self._update_product(api_products)

    def update_scopes(self, scopes: list, api_products):
        """ Update the product scopes """
        self.scopes = scopes
        return self._update_product(api_products)

    def update_proxies(self, proxies: list, api_products):
        """ Update the product assigned proxies """
        self.proxies = proxies
        return self._update_product(api_products)

    def update_paths(self, paths: list, api_products):
        """ Update the product assigned paths """
        self.api_resources = paths
        return self._update_product(api_products)

    def create_new_product(self, api_products) -> dict:
        """ Create a new developer product in apigee """
    
        resp = api_products.post_products(body=self._product())
        LOGGER.info(f'Created product with name: {resp.get("name")}')

        return resp

    def _update_product(self, api_products) -> dict:
        """ Update product """
        # LOGGER.info(f'New product value: {self._product()}')
        resp = api_products.put_product_by_name(product_name=self.name, body=self._product())
        LOGGER.info(f'update response: {resp}')
        return resp

    def get_product_details(self, api_products) -> dict:
        """ Return all available details for the product """
        resp = api_products.get_product_by_name(product_name=self.name)

        return resp

    def destroy_product(self, api_products) -> dict:
        """ Delete the product """        
        resp = api_products.delete_product_by_name(product_name=self.name)

        return resp
