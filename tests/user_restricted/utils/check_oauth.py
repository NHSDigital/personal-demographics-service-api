import requests
from ..configuration import config
from api_test_utils.oauth_helper import OauthHelper


class CheckOauth:
    def __init__(self):
        super(CheckOauth, self).__init__()
        self.session = requests.Session()
        self.base_uri = f"{config.BASE_URL}/{config.OAUTH_PROXY}"

    @staticmethod
    def get_token_response():
        raise RuntimeError(f"redirect uri!!!! {config.REDIRECT_URI}")
        oauth = OauthHelper(config.CLIENT_ID, config.CLIENT_SECRET, config.REDIRECT_URI)
        token_resp = oauth.get_authenticated_with_mock_auth(user=config.IDENTITY_SERVICE_MOCK_USER_ID)
        return token_resp
