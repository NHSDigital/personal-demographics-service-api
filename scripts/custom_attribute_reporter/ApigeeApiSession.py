"""
Helper session class built on top of requests to reuse authentication and base URL details etc.
"""
from requests import Session
from urllib.parse import urljoin


# Note: this class is built on top of Python requests, which is blocking. This works fine for PDS.
# But if timeliness is a concern i.e. you have a very large number of connected apps, consider using a library such as
# aiohttp which can be run in an async manner.
class ApigeeApiSession(Session):
    def __init__(self, apigee_org: str, auth_token: str):
        super().__init__()
        self._base_url = f"https://api.enterprise.apigee.com/v1/organizations/{apigee_org}/"
        self.headers.update({"Authorization": f"Bearer {auth_token}"})

    def request(self, method: str, url: str, *args, **kwargs):
        joined_url = urljoin(self._base_url, url)
        return super().request(method, joined_url, *args, **kwargs)
