from requests import Session
from urllib.parse import urljoin

class ApigeeApiSession(Session):
    def __init__(self, base_url: str, auth_token: str):
        super().__init__()
        self._base_url = base_url
        self.headers.update({"Authorization": f"Bearer {auth_token}"})

    def request(self, method, url, *args, **kwargs):
        joined_url = urljoin(self._base_url, url)
        return super().request(method, joined_url, *args, **kwargs)
