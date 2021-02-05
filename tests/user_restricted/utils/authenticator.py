from urllib import parse
from ..configuration import config


class Authenticator:
    def __init__(self, session):
        self.session = session
        self.data = self._get_request_data()

    def _simulated_oauth_prerequisite(self):
        """Request the login page and retrieve the callback url and assigned state"""
        login_page_response = self.session.get(config.ENDPOINTS['authenticate'])

        if login_page_response.status_code != 200:
            raise ValueError("Invalid login page response status code")

        # Login
        params = {
            'client_id': config.CLIENT_ID,
            'redirect_uri': config.REDIRECT_URI,
            'response_type': 'code',
            'state': '1234567890'
        }

        success_response = self.session.get(config.ENDPOINTS['authorize'], params=params, allow_redirects=False)

        # Confirm request was successful
        if success_response.status_code != 302:
            raise ValueError(f"Getting an error: {success_response.status_code} : {success_response.text}")

        call_back_url = success_response.headers.get('Location')
        state = self.get_params_from_url(call_back_url)['state']
        return call_back_url, state

    def _get_request_data(self) -> dict:
        """Get the request data required for authenticating with a given provider"""
        url, state = self._simulated_oauth_prerequisite()

        return {
            'url': url,
            'headers': {'Content-Type': 'application/x-www-form-urlencoded'},
            'params': {},
            'payload': {'state': state}
        }

    def authenticate(self):
        """Send authentication request"""
        sign_in_response = self.session.post(
            self.data['url'],
            headers=self.data['headers'],
            params=self.data['params'],
            data=self.data['payload'],
            allow_redirects=False
        )

        # Confirm request was successful
        if sign_in_response.status_code != 302:
            raise ValueError(f"Failed to get authenticated "
                             f"with {sign_in_response.status_code} : {sign_in_response.text}")

        return sign_in_response

    def get_code_from_provider(self, sign_in_response) -> str:
        """Retrieve the code value from an authentication response"""
        # Extract url from location header and make the call back request
        callback_url = sign_in_response.headers.get('Location')
        callback_response = self.session.get(callback_url, allow_redirects=False)

        # Confirm request was successful
        if callback_response.status_code != 302:
            raise ValueError(f"Callback request failed with {callback_response.status_code} : {callback_response.text}")

        # Return code param from location header
        return self.get_params_from_url(callback_response.headers.get('Location'))['code']

    @staticmethod
    def get_params_from_url(url: str) -> dict:
        """Returns all the params and param values from a given url as a dictionary"""
        return dict(parse.parse_qsl(parse.urlsplit(url).query))
