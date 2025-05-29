"""
Helper session class built on top of requests to reuse authentication and base URL details etc.
"""
from requests import Session
from urllib.parse import urljoin


class ApigeeApiSession(Session):
    def __init__(self, apigee_org: str, auth_token: str):
        super().__init__()
        self._base_url = f"https://api.enterprise.apigee.com/v1/organizations/{apigee_org}/"
        self.headers.update({"Authorization": f"Bearer {auth_token}"})

    def request(self, method, url, *args, **kwargs):
        joined_url = urljoin(self._base_url, url)
        return super().request(method, joined_url, *args, **kwargs)
