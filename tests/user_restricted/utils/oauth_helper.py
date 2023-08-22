from os import environ
import re
import requests
import json
from lxml import html
from uuid import uuid4
from time import time
from ast import literal_eval
from urllib.parse import urlparse, parse_qs
import asyncio
import urllib
import jwt  # pyjwt
from aiohttp.client_exceptions import ContentTypeError
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from api_test_utils.api_session_client import APISessionClient
from . import env


class OauthHelper:
    """A helper class to interact with the different OAuth flows"""

    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.proxy = self._get_proxy()
        self.base_uri = self._get_base_uri()

    @staticmethod
    def _get_proxy():
        _proxy = environ.get("OAUTH_PROXY", "not-set").strip()
        if _proxy == "not-set":
            raise RuntimeError("\nOAUTH_PROXY is missing from environment variables\n")
        return _proxy

    def _get_base_uri(self):
        _uri = environ.get("OAUTH_BASE_URI", "not-set").strip()
        if _uri == "not-set":
            raise RuntimeError(
                "\nOAUTH_BASE_URI is missing from environment variables\n"
            )
        return f"{_uri}/{self.proxy}"

    @staticmethod
    def _read_file(file):
        with open(file, "r") as f:
            contents = f.read()
        if not contents:
            raise RuntimeError(f"Contents of file {file} is empty.")
        return contents

    def _get_private_key(self):
        """Return the contents of a private key"""
        _path = environ.get("JWT_PRIVATE_KEY_ABSOLUTE_PATH", "not-set").strip()
        if _path == "not-set":
            raise RuntimeError(
                "\nJWT_PRIVATE_KEY_ABSOLUTE_PATH is missing from environment variables\n"
            )
        return self._read_file(_path)

    def _get_id_token_private_key(self):
        """Return the contents of a private key"""
        _path = environ.get("ID_TOKEN_PRIVATE_KEY_ABSOLUTE_PATH", "not-set").strip()
        if _path == "not-set":
            raise RuntimeError(
                "\nID_TOKEN_PRIVATE_KEY_ABSOLUTE_PATH is missing from environment variables\n"
            )
        return self._read_file(_path)

    async def get_authenticated_with_simulated_auth(self, auth_scope: str = ""):
        """Get the code parameter value required to post to the oauth /token endpoint"""
        authenticator = _SimulatedAuthFlow(
            self.base_uri, self.client_id, self.redirect_uri
        )
        return await authenticator.authenticate(auth_scope=auth_scope)

    def get_authenticated_with_mock_auth(
        self, user: str = "9999999999"
    ) -> str:
        session = requests.Session()

        resp = session.get(
            f"{self.base_uri}/authorize",
            params={
                "client_id": self.client_id,
                "redirect_uri": self.redirect_uri,
                "response_type": "code",
                "state": "1234567890",
            },
            verify=False
        )

        if resp.status_code != 200:
            raise RuntimeError(json.dumps(resp.json(), indent=2))

        tree = html.fromstring(resp.content.decode())

        form = tree.get_element_by_id("kc-form-login")
        url = form.action
        resp2 = session.post(url, data={"username": user})

        qs = urlparse(resp2.history[-1].headers["Location"]).query
        auth_code = parse_qs(qs)["code"]
        if isinstance(auth_code, list):
            auth_code = auth_code[0]

        resp3 = session.post(
            f"{self.base_uri}/token",
            data={
                "grant_type": "authorization_code",
                "code": auth_code,
                "redirect_uri": self.redirect_uri,
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            },
        )
        return resp3.json()

    async def _get_default_authorization_code_request_data(
        self, grant_type, timeout: int = 5000, refresh_token: str = None
    ) -> dict:
        """Get the default data required for an authorization_code or refresh_token request"""
        form_data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": grant_type,
        }
        if refresh_token:
            form_data["refresh_token"] = refresh_token
            form_data["_refresh_token_expiry_ms"] = timeout
        else:
            form_data["redirect_uri"] = self.redirect_uri
            form_data["code"] = await self.get_authenticated_with_simulated_auth()
            form_data["_access_token_expiry_ms"] = timeout
        return form_data

    @staticmethod
    async def _get_default_jwt_request_data(
        grant_type: str, _jwt: bytes, id_token_jwt: bytes = None
    ) -> dict:
        """Get the default data required for a client credentials or token exchange request"""
        if grant_type.strip().lower() == "token_exchange":
            if not id_token_jwt:
                # This argument is required if you are using token exchange
                raise TypeError("missing 1 required keyword argument: 'id_token_jwt'")
            return {
                "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
                "subject_token_type": "urn:ietf:params:oauth:token-type:id_token",
                "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
                "subject_token": id_token_jwt,
                "client_assertion": _jwt,
            }
        # Get the default data required for a client credentials request
        return {
            "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
            "client_assertion": _jwt,
            "grant_type": grant_type,
        }

    @staticmethod
    async def _retry_requests(make_request, max_retries):
        retry_codes = {429, 503, 409}
        for retry_number in range(max_retries):
            resp = await make_request()
            if resp.status in retry_codes:
                await asyncio.sleep(2 ** retry_number - 1)
                continue
            return resp
        raise TimeoutError("Maximum retry limit hit.")

    async def hit_oauth_endpoint(
        self, method: str, endpoint: str, base_uri=None, **kwargs
    ) -> dict:
        """Send a request to a OAuth endpoint"""
        if not base_uri:
            base_uri = self.base_uri

        async with APISessionClient(base_uri) as session:
            request_method = (session.post, session.get)[
                method.lower().strip() == "get"
            ]
            resp = await self._retry_requests(
                lambda: request_method(endpoint, **kwargs), 5
            )
            try:
                body = await resp.json()
                _ = body.pop(
                    "message_id", None
                )  # Remove the unique message id if the response is na error
            except ContentTypeError:
                # Might be html or text response
                body = await resp.read()

                if isinstance(body, bytes):
                    # Convert into a string
                    body = str(body, "UTF-8")
                    try:
                        # In case json response was of type bytes
                        body = literal_eval(body)
                    except SyntaxError:
                        # Continue
                        pass

            return {
                "method": resp.method,
                "url": resp.url,
                "status_code": resp.status,
                "body": body,
                "headers": dict(resp.headers.items()),
                "history": resp.history,
            }

    async def get_token_response(self, grant_type: str, **kwargs) -> dict:
        """Get a token response through any of the available OAuth grant type flows"""
        if "data" not in kwargs:
            # Get defaults
            func = {
                "authorization_code": self._get_default_authorization_code_request_data,
                "refresh_token": self._get_default_authorization_code_request_data,
                "client_credentials": self._get_default_jwt_request_data,
                "token_exchange": self._get_default_jwt_request_data,
            }.get(grant_type)

            kwargs["data"] = await func(grant_type, **kwargs)
        return await self.hit_oauth_endpoint("post", "token", data=kwargs["data"])

    def create_jwt(
        self,
        kid: str,
        signing_key: str = None,
        claims: dict = None,
        algorithm: str = "RS512",
        client_id: str = None,
        **kwargs,
    ) -> bytes:
        """Create a Json Web Token"""
        if client_id is None:
            # Get default client id
            client_id = self.client_id
        if not signing_key:
            # Get default key
            signing_key = self._get_private_key()

        if not claims:
            # Get default claims
            claims = {
                "sub": client_id,
                "iss": client_id,
                "jti": str(uuid4()),
                "aud": f"{self.base_uri}/token",
                "exp": int(time()) + 5,
            }

        headers = ({}, {"kid": kid})[kid is not None]

        if kwargs.get("headers", None):
            headers = {**headers, **kwargs["headers"]}
        return jwt.encode(claims, signing_key, algorithm=algorithm, headers=headers)

    def create_id_token_jwt(
        self,
        kid: str = "identity-service-tests-1",
        signing_key: str = None,
        claims: dict = None,
        algorithm: str = "RS256",
        headers: dict = None,
    ) -> bytes:
        """Get the default ID token JWT"""
        if not signing_key:
            # Get default key
            signing_key = self._get_id_token_private_key()

        if not claims:
            # Get defaults
            claims = {
                "at_hash": "tf_-lqpq36lwO7WmSBIJ6Q",
                "sub": "787807429511",
                "auditTrackingId": "91f694e6-3749-42fd-90b0-c3134b0d98f6-1546391",
                "amr": ["N3_SMARTCARD"],
                "iss": "https://am.nhsint.auth-ptl.cis2.spineservices.nhs.uk:443/"
                "openam/oauth2/realms/root/realms/NHSIdentity/realms/Healthcare",
                "tokenName": "id_token",
                "aud": "969567331415.apps.national",
                "c_hash": "bc7zzGkClC3MEiFQ3YhPKg",
                "acr": "AAL3_ANY",
                "org.forgerock.openidconnect.ops": "-I45NjmMDdMa-aNF2sr9hC7qEGQ",
                "s_hash": "LPJNul-wow4m6Dsqxbning",
                "azp": "969567331415.apps.national",
                "auth_time": 1610559802,
                "realm": "/NHSIdentity/Healthcare",
                "exp": int(time()) + 6000,
                "tokenType": "JWTToken",
                "iat": int(time()) - 100,
            }
        return self.create_jwt(
            kid=kid,
            signing_key=signing_key,
            claims=claims,
            algorithm=algorithm,
            headers=headers,
        )


class _SimulatedAuthFlow:
    def __init__(self, base_uri: str, client_id: str, redirect_uri: str):
        self.base_uri = base_uri
        self.client_id = client_id
        self.redirect_uri = redirect_uri

    async def _get_state(self, request_state: str, auth_scope: str = "") -> str:
        """Send an authorize request and retrieve the state"""
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "state": request_state,
            "scope": auth_scope,
        }

        async with APISessionClient(self.base_uri) as session:
            async with session.get("authorize", params=params) as resp:
                body = await resp.read()
                if resp.status != 200:
                    headers = dict(resp.headers.items())
                    throw_friendly_error(
                        message="unexpected response, unable to authenticate with simulated oauth",
                        url=resp.url,
                        status_code=resp.status,
                        response=body,
                        headers=headers,
                    )

                state = dict(resp.url.query)["state"]

                # Confirm state is converted to a cryptographic value
                assert state != request_state
                return state

    async def authenticate(self, request_state: str = str(uuid4()), auth_scope: str = "") -> str:
        """Authenticate and retrieve the code value"""
        state = await self._get_state(request_state, auth_scope=auth_scope)
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": "openid",
            "state": state,
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        payload = {"state": state}

        mock_proxy_base_uri = (
            f"https://{env.api_env()}.api.service.nhs.uk/mock-nhsid-jwks"
        )
        async with APISessionClient(mock_proxy_base_uri) as session:
            async with session.post(
                "simulated_auth",
                params=params,
                data=payload,
                headers=headers,
                allow_redirects=False,
            ) as resp:
                if resp.status != 302:
                    body = await resp.json()
                    headers = dict(resp.headers.items())
                    throw_friendly_error(
                        message="unexpected response, unable to authenticate with simulated oauth",
                        url=resp.url,
                        status_code=resp.status,
                        response=body,
                        headers=headers,
                    )

                redirect_uri = resp.headers["Location"]
                if "-pr-" in self.base_uri:
                    pr_number = re.search("(?<=oauth2).*$", self.base_uri).group()
                    redirect_uri = redirect_uri.replace("oauth2", f"oauth2{pr_number}")

                async with session.get(
                    redirect_uri,
                    allow_redirects=False,
                    headers={"Auto-Test-Header": "flow-callback"},
                ) as callback_resp:
                    headers = dict(callback_resp.headers.items())
                    # Confirm request was successful
                    if callback_resp.status != 302:
                        body = await callback_resp.read()
                        throw_friendly_error(
                            message="unexpected response, unable to authenticate with simulated oauth",
                            url=resp.url,
                            status_code=callback_resp.status,
                            response=body,
                            headers=headers,
                        )

                    # Get code value from location parameters
                    query = headers["Location"].split("?")[1]
                    params = {
                        x[0]: x[1] for x in [x.split("=") for x in query.split("&")]
                    }
                    return params["code"]


class _RealAuthFlow:
    def __init__(
        self, base_uri: str, client_id: str, client_secret: str, redirect_uri: str
    ):
        self.base_uri = base_uri
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri

    async def _get_state(self, request_state: str) -> str:
        """Send an authorize request and retrieve the state"""
        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "state": request_state,
        }

        async with APISessionClient(self.base_uri) as session:
            async with session.get("authorize", params=params) as resp:
                body = await resp.read()
                if resp.status != 200:
                    headers = dict(resp.headers.items())
                    throw_friendly_error(
                        message="unexpected response, unable to authenticate with simulated oauth",
                        url=resp.url,
                        status_code=resp.status,
                        response=body,
                        headers=headers,
                    )

                state = dict(resp.url.query)["state"]

                # Confirm state is converted to a cryptographic value
                assert state != request_state
                return state

    async def authenticate(
        self,
        user: str,
        webdriver_session: WebDriver = None,
        request_state: str = str(uuid4()),
    ) -> str:
        """Authenticate and retrieve the code value"""
        # state = await self._get_state(request_state)
        params = urllib.parse.urlencode(
            [
                (k, v)
                for k, v in {
                    "response_type": "code",
                    "client_id": self.client_id,
                    "redirect_uri": self.redirect_uri,
                    "state": request_state,
                }.items()
            ]
        )

        authorize_url = f"{self.base_uri}/authorize?{params}"

        webdriver_session.get(authorize_url)
        webdriver_session.implicitly_wait(1)
        username = webdriver_session.find_element(By.ID, "username")
        username.send_keys(user + Keys.ENTER)
        webdriver_session.implicitly_wait(5)
        code = dict(
            urllib.parse.parse_qsl(
                urllib.parse.urlsplit(webdriver_session.current_url).query
            )
        )["code"]
        return code


def throw_friendly_error(message: str, url: str, status_code: int, response: str, headers: dict) -> Exception:
    raise Exception(f"\n{'*' * len(message)}\n"
                    f"MESSAGE: {message}\n"
                    f"URL: {url}\n"
                    f"STATUS CODE: {status_code}\n"
                    f"RESPONSE: {response}\n"
                    f"HEADERS: {headers}\n"
                    f"{'*' * len(message)}\n")
