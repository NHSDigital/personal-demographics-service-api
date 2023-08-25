from .apigee_api import ApigeeApi

class ApigeeApiDeveloperApps(ApigeeApi):
    """ A simple class to help facilitate CRUD operations for developer apps in Apigee """

    def __init__(self, org_name: str = "nhsd-nonprod", developer_email: str = "apm-testing-internal-dev@nhs.net"):
        super().__init__(org_name)
        self.developer_email = developer_email

        self.client_id = None
        self.client_secret = None
        self.callback_url = None

        self.app_base_uri = f"{self.base_uri}/developers/{self.developer_email}"

        self.default_params = {
            "org_name": self.org_name,
            "developer_email": self.developer_email,
        }

    def create_new_app(self, callback_url, status, developer_apps) -> dict:
        """ Create a new developer app in apigee """
        self.callback_url = callback_url

        data = {
            "attributes": [{"name": "DisplayName", "value": self.name}],
            "callbackUrl": self.callback_url,
            "name": self.name,
            "status": status
        }

        return developer_apps.create_app(email=self.developer_email, body=data)

    def add_api_product(self, products: list, developer_apps) -> dict:
        """ Add a number of API Products to the app """
        data = {
            "apiProducts": products,
            "name": self.name,
            "status": "approved"
        }
        return developer_apps.put_app_by_name(email=self.developer_email, app_name=self.name, body=data)

    def set_custom_attributes(self, attributes: dict, developer_apps) -> dict:
        """ Replaces the current list of attributes with the attributes specified """
        custom_attributes = [{"name": "DisplayName", "value": self.name}]
        for key, value in attributes.items():
            custom_attributes.append({"name": key, "value": value})
        data = {"attribute": custom_attributes}
        return developer_apps.post_app_attributes(email=self.developer_email, app_name=self.name, body=data)

    def update_custom_attribute(self, attribute_name: str, attribute_value: str, developer_apps) -> dict:
        """ Update an existing custom attribute """
        data = {
            "value": attribute_value
        }
        return developer_apps.post_app_attribute_by_name(
            email=self.developer_email,
            app_name=self.name,
            attribute_name=attribute_name,
            body=data
        )

    def delete_custom_attribute(self, attribute_name: str, developer_apps) -> dict:
        """ Delete a custom attribute """
        return developer_apps.delete_app_attribute_by_name(
            email=self.developer_email,
            app_name=self.name,
            attribute_name=attribute_name
        )

    def get_custom_attributes(self, developer_apps) -> dict:
        """ Get the list of custom attributes assigned to the app """
        return developer_apps.get_app_attributes(email=self.developer_email, app_name=self.name)

    def get_app_details(self, developer_apps) -> dict:
        """ Return all available details for the app """
        return developer_apps.get_app_by_name(email=self.developer_email, app_name=self.name)

    def get_client_id(self):
        """ Get the client id """
        if not self.client_id:
            raise RuntimeError("\nthe application has not been created! \n"
                               "please invoke 'create_new_app()' method before requesting the client_id")
        return self.client_id

    def get_client_secret(self):
        """ Get the client secret """
        if not self.client_secret:
            raise RuntimeError("\nthe application has not been created! \n"
                               "please invoke 'create_new_app()' method before requesting the client secret")
        return self.client_secret

    def get_callback_url(self) -> str:
        """ Get the callback url """
        if not self.callback_url:
            raise RuntimeError("\nthe application has not been created! \n"
                               "please invoke 'create_new_app()' method before requesting the callback url")
        return self.callback_url

    def destroy_app(self, developer_apps) -> dict:
        """ Delete the app """
        return developer_apps.delete_app_by_name(email=self.developer_email, app_name=self.name)
