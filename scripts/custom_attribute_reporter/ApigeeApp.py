"""Simple representation of an Apigee App containing attributes we care about such as rate limit, flow vars etc."""


class ApigeeApp:
    BASE_URL = "https://apigee.com/organizations"

    def __init__(
        self,
        app_id: str,
        name: str,
        rate_limit: dict,
        requested_apim_flow_vars: dict,
        apigee_org: str
    ):
        self.id = app_id
        self.name = name
        self.rate_limit = rate_limit
        self.requested_apim_flow_var = requested_apim_flow_vars
        self.url = f"{ApigeeApp.BASE_URL}/{apigee_org}/apps/details/{app_id}"

    def __str__(self):
        return (f"###\nApp ID: {self.id}\nDisplay Name: {self.name}\nRate Limit: {self.rate_limit}\nAPIM Flow Vars: "
                f"{self.requested_apim_flow_var}\n###\n")
