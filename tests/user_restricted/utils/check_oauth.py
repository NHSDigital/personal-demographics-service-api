from .authenticator import Authenticator
import requests
import json
from ..configuration import config


class CheckOauth:
    def __init__(self):
        super(CheckOauth, self).__init__()
        self.session = requests.Session()

    def get_authenticated(self) -> str:
        """Get the code parameter value required to post to the oauth /token endpoint"""
        authenticator = Authenticator(self.session)
        response = authenticator.authenticate()
        code = authenticator.get_code_from_provider(response)
        return code

    def get_token_response(self, timeout: int = 5000, grant_type: str = 'authorization_code', refresh_token: str = ""):
        data = {
            'client_id': config.CLIENT_ID,
            'client_secret': config.CLIENT_SECRET,
            'grant_type': grant_type,
        }
        if refresh_token != "":
            data['refresh_token'] = refresh_token
            data['_refresh_token_expiry_ms'] = timeout
        else:
            data['redirect_uri'] = config.REDIRECT_URI
            data['code'] = self.get_authenticated()
            data['_access_token_expiry_ms'] = timeout

        response = self.session.post(config.ENDPOINTS['token'], data=data)
        if response.status_code != 200:
            raise Exception(f'/token endpoint failed: {response.status_code} : {response.text}')

        return json.loads(response.text)
