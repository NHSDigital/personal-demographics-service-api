import requests
import urllib.parse as urlparse
from urllib.parse import parse_qs

class Auth:

    def __init__(self, url, callback_url, client_id, client_secret):
        self.session = requests.Session()
        self.base_url = url
        self.callback_url = callback_url
        self.client_id = client_id
        self.client_secret = client_secret

    def login(self):
        state = self.get_state()
        code = self.get_auth_code(state)
        self.get_access_token(code, state)

    def get_state(self):
        url = f"{self.base_url}/oauth2/authorize?client_id={self.client_id}&redirect_uri={self.callback_url}&response_type=code&state=1234567890"
        response = self.session.get(url)
        parsed = urlparse.urlparse(response.url)
        return parse_qs(parsed.query)['state'][0]

    def get_auth_code(self, state):
        url = f"{self.base_url}/oauth2/simulated_auth?response_type=code&client_id=some-client-id&redirect_uri={self.base_url}/callback&scope=openid&state={state}"
        headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip,deflate",
            "Cache-Control": "no-cache",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        payload = {
            "state": state
        }
        response = self.session.post(url, data=payload, headers=headers, allow_redirects=False)
        parsed = urlparse.urlparse(response.headers['Location'])
        code = parse_qs(parsed.query)["code"][0]
        return code

    def get_access_token(self, code, state):
        url = f"{self.base_url}/oauth2/token"
        headers = {
            "Accept": "*/*",
            "connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        payload = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.callback_url,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        response = self.session.post(url, data=payload, headers=headers)
        print(response.status_code)
        print(response.url)
        print(response.text)
