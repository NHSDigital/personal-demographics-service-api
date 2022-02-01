import requests
import json
from ..configuration import config
from api_test_utils.oauth_helper import OauthHelper


class CheckOauth:
    def __init__(self):
        super(CheckOauth, self).__init__()
        self.session = requests.Session()
        self.base_uri = f"{config.BASE_URL}/{config.IDENTITY_SERVICE}"

    @staticmethod
    async def get_authenticated(webdriver_session) -> str:
        """Get the code parameter value required to post to the oauth /token endpoint"""

        oauth = OauthHelper(config.CLIENT_ID, config.CLIENT_SECRET, config.REDIRECT_URI)

        code = await oauth.get_authenticated_with_mock_auth(user=config.IDENTITY_SERVICE_MOCK_USER_ID,
                                                            webdriver_session=webdriver_session)

        return code

    async def get_token_response(self, webdriver_session, grant_type: str = 'authorization_code',
                                 refresh_token: str = ""):
        data = {
            'client_id': config.CLIENT_ID,
            'client_secret': config.CLIENT_SECRET,
            'grant_type': grant_type,
        }
        if refresh_token != "":
            data['refresh_token'] = refresh_token
        else:
            data['redirect_uri'] = config.REDIRECT_URI
            data['code'] = await self.get_authenticated(webdriver_session)

        response = self.session.post(config.ENDPOINTS['token'], data=data)
        if response.status_code != 200:
            raise Exception(f'/token endpoint failed: {response.status_code} : {response.text}')

        return json.loads(response.text)
