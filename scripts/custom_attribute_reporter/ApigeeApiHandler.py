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

    def get_app_ids_for_product(self, product_name: str, count_per_page: int = 100) -> set[str]:
        """
        https://apidocs.apigee.com/docs/api-products/1/routes/organizations/%7Borg_name%7D/apiproducts/
        %7Bapiproduct_name%7D/get
        PLEASE NOTE: there are 2 issues with Apigee's above documentation
        1. The start key query parameter is actually the App ID rather than the name as stated in the docs
        2. Not an error per se, but the start key is inclusive so appropriate handling has been put in for this
        """
        product_path = f"{self.PRODUCT_ENDPOINT}/{product_name}"
        default_query_params = {
            "query": "list",
            "entity": "apps",
            "count": count_per_page,
        }

        response = self._api_session.get(product_path, params=default_query_params)

        if response.status_code != http.client.OK:
            raise HTTPError(f'Something went wrong:\n{response.status_code}\n{response.text}')

        app_ids_in_page = response.json()
        all_app_ids = []

        while True:
            all_app_ids.extend(app_ids_in_page)

            if len(app_ids_in_page) < count_per_page:
                return set(all_app_ids)

            response = self._api_session.get(
                product_path,
                params=default_query_params | {"startkey": app_ids_in_page[-1]}
            )

            if response.status_code != http.client.OK:
                raise HTTPError(f'Something went wrong:\n{response.status_code}\n{response.text}')

            app_ids_in_page = response.json()

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
