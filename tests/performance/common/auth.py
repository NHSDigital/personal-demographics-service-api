import requests
import json
import asyncio
import urllib.parse as urlparse
from urllib.parse import parse_qs
from bs4 import BeautifulSoup

# Move to parameters 
BASE_URL = "https://internal-dev.api.service.nhs.uk"

class Auth:

    def __init__(self):
        self.session = requests.Session()

    def login(self):
        state = self.get_state()
        credentials = self.get_access_token(state)
        return credentials

    def get_state(self):
        url = f"{BASE_URL}/oauth2/authorize?client_id=Too5BdPayTQACdw1AJK1rD4nKUD0Ag7J&redirect_uri=https%3A%2F%2Fnhsd-apim-testing-internal-dev.herokuapp.com%2Fcallback&response_type=code&state=1234567890"
        response = self.session.get(url)
        parsed = urlparse.urlparse(response.url)
        return parse_qs(parsed.query)['state'][0]

    def get_access_token(self, state):
        url = f"{BASE_URL}/oauth2/simulated_auth?response_type=code&client_id=some-client-id&redirect_uri={BASE_URL}/callback&scope=openid&state={state}"
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Accept-Encoding": "gzip,deflate,br",
            "Cache-Control": "no-cache",
            "Content-Type": "application/x-www-form-urlencoded",
        }
        payload = {
            "state": state
        }
        response = self.session.post(url, data=payload, headers=headers)
        soup = BeautifulSoup(response.text, features="html.parser")
        credentials = soup.find('pre').text
        credentials = credentials.replace("\'", "\"")
        return json.loads(credentials)
        
