"""
Handler class for managing interactions with the Apigee API
"""
import http.client

from requests import HTTPError

from .ApigeeApiSession import ApigeeApiSession


class ApigeeApiHandler:
    APP_ENDPOINT = "apps"
    PRODUCT_ENDPOINT = "apiproducts"

    def __init__(self, apigee_org: str, auth_token: str):
        self._api_session = ApigeeApiSession(
            apigee_org,
            auth_token
        )

    def get_app_ids_for_product(self, product_name: str) -> list[str]:
        """https://apidocs.apigee.com/docs/api-products/1/routes/organizations/%7Borg_name%7D/apiproducts
        /%7Bapiproduct_name%7D/get"""
        product_path = f"{self.PRODUCT_ENDPOINT}/{product_name}"
        apps_query = {
            "query": "list",
            "entity": "apps"
        }

        response = self._api_session.get(product_path, params=apps_query)

        if response.status_code != http.client.OK:
            raise HTTPError(f'Something went wrong:\n{response.status_code}\n{response.text}')

        return response.json()

    def get_app_metadata(
        self,
        app_id: str
    ) -> dict:
        """https://apidocs.apigee.com/docs/apps/1/routes/organizations/%7Borg_name%7D/apps/%7Bapp_id%7D/get"""
        app_path = f"{self.APP_ENDPOINT}/{app_id}"
        response = self._api_session.get(app_path)

        if response.status_code != http.client.OK:
            raise HTTPError(f'Something went wrong for {app_path}:\n{response.status_code}\n{response.text}')

        return response.json()
