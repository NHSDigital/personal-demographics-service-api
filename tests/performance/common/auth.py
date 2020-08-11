import requests
import json
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
        redirect = self.get_redirect_callback(state)
        code = self.get_auth_code(redirect)
        return self.get_access_token(code)

    def get_state(self):
        url = f"{self.base_url}/oauth2/authorize"
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.callback_url,
            "response_type": "code",
            "state": "1234567890"
        }
        response = self.session.get(url, params=params)
        parsed = urlparse.urlparse(response.url)
        return parse_qs(parsed.query)['state'][0]

    def get_redirect_callback(self, state):
        url = f"{self.base_url}/oauth2/simulated_auth"
        params = {
            "response_type": "code",
            "client_id": "some-client-id",
            "redirect_uri": f"{self.base_url}/callback",
            "scope": "openid",
            "state": state
        }
        headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip,deflate",
            "Cache-Control": "max-age=0",
            "Content-Type": "application/x-www-form-urlencoded",
            "Upgrade-Insecure-Requests": "1"
        }
        payload = {
            "state": state
        }
        response = self.session.post(url, params=params, data=payload, headers=headers, allow_redirects=False)
        redirect = response.headers['Location']
        return redirect

    def get_auth_code(self, redirect_url):
        response = self.session.get(redirect_url, allow_redirects=False)
        parsed = urlparse.urlparse(response.headers['Location'])
        return parse_qs(parsed.query)["code"][0]

    def get_access_token(self, code):
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
        credentials = json.loads(response.text)
        return credentials
