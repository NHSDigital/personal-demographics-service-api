import requests
from json import loads, JSONDecodeError
from urllib import parse
from re import sub
from urllib.parse import urlparse, urlencode
from typing import Optional
from typing import Union


class GenericRequest:
    """This is a base class to facilitate testing an API.
    It contains reusable components & functions that can be shared between different APIs"""

    def __init__(self):
        self.session = requests.Session()

    def get_response(self, verb: str, url: str, **kwargs) -> requests.Response:
        """Verify the arguments and then send a request and return the response"""
        if not self.is_url(url):
            raise RuntimeError("Endpoint not found")

        # Verify http verb is valid
        if verb.lower() not in {'post', 'get', 'put', 'patch'}:
            raise RuntimeError(f"Verb: {verb} is invalid")

        func = (((self.get,  # else
                  self.patch)[verb.lower() == 'patch'],
                 self.put)[verb.lower() == 'put'],
                self.post)[verb.lower() == 'post']

        # Get response
        return func(url, **kwargs)

    @staticmethod
    def check_response(resp, expected_status_code, expected_response, headers=None, redirects=None):
        if isinstance(expected_response, list):
            resp['body'] = list(resp['body'].keys())

        message = f"\n{'*' * 10}\n" \
                  f"REQUEST: {resp}\n" \
                  f"EXPECTED STATUS CODE: {expected_status_code}\n" \
                  f"ACTUAL STATUS CODE: {resp['status_code']}\n" \
                  f"EXPECTED RESPONSE: {expected_response}\n" \
                  f"ACTUAL RESPONSE: {resp['body']}\n"

        assert resp['status_code'] == expected_status_code, message
        assert resp['body'] == expected_response, message

        if headers:
            assert resp['headers'] == headers, message
        if redirects:
            assert resp['history'] == redirects, message
        return True

    @staticmethod
    async def send_request_and_check_output(expected_status_code, expected_response, function, *args, **kwargs):
        resp = await function(*args, **kwargs)

        if isinstance(expected_response, list):
            resp['body'] = list(resp['body'].keys())

        assert resp['status_code'] == expected_status_code and resp['body'] == expected_response, \
            f"\nREQUEST: {resp}\n" \
            f"EXPECTED STATUS CODE: {expected_status_code}\n" \
            f"ACTUAL STATUS CODE: {resp['status_code']}\n" \
            f"EXPECTED RESPONSE: {expected_response}\n" \
            f"ACTUAL RESPONSE: {resp['body']}\n"
        return True

    @staticmethod
    def is_url(url: str) -> bool:
        """Check if a string looks like a URL"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False

    @staticmethod
    def _validate_response(response: requests.Response) -> None:
        """Verifies the response provided is of a valid response type"""
        if not type(response) == requests.models.Response:
            raise TypeError("Expected response type object for response argument")

    @staticmethod
    def check_params(params, expected_params):
        return all(params.get(key) and params[key] == value for key, value in expected_params.items())

    def verify_params_exist_in_url(self, params: list, url: str) -> bool:
        _params = self.get_params_from_url(url)
        for param in params:
            if not _params[param]:
                return False
        return True

    @staticmethod
    def _verify_status_code(status_code: Union[int, str]) -> None:
        """Verifies the status code provided is a valid status code"""
        if not type(status_code) == int:
            try:
                int(status_code)
            except ValueError:
                raise TypeError("Status code must only consist of numbers")
        else:
            if len(str(status_code)) != 3:
                raise TypeError("Status code must be a 3 digit number")

    def get(self, url: str, **kwargs) -> requests.Response:
        """Sends a get request and returns the response"""
        try:
            return self.session.get(url, **kwargs)
        except requests.ConnectionError:
            raise Exception(f"the url: {url} does not exist or is invalid")

    def post(self, url: str, **kwargs) -> requests.Response:
        """Sends a post request and returns the response"""
        try:
            return self.session.post(url, **kwargs)
        except requests.ConnectionError:
            raise Exception(f"the url: {url} does not exist or is invalid")

    def put(self, url: str, **kwargs) -> requests.Response:
        """Sends a put request and returns the response"""
        try:
            return self.session.put(url, **kwargs)
        except requests.ConnectionError:
            raise Exception(f"the url: {url} does not exist or is invalid")

    def patch(self, url: str, **kwargs) -> requests.Response:
        """Sends a patch request and returns the response"""
        try:
            return self.session.patch(url, **kwargs)
        except requests.ConnectionError:
            raise Exception(f"the url: {url} does not exist or is invalid")

    def get_redirects(self, response: requests.Response) -> dict:
        """Returns a list of response objects holding the history of request (url)"""
        self._validate_response(response)

        redirects = {}
        if response.history:
            for i, resp in enumerate(response.history):
                redirects[i] = {
                    "status_code": resp.status_code,
                    "url": resp.url,
                    "headers": resp.headers,
                }
        return redirects

    def verify_response_keys(self, response: requests.Response, expected_status_code: int, expected_keys: list) -> bool:
        """Check a given response is returning the correct keys.
        In case the content is dynamic we can only check the keys and not the values"""
        self._validate_response(response)

        data = loads(response.text)

        if "error" in data:
            assert data == expected_keys
        else:
            actual_keys = list(data.keys())
            assert sorted(actual_keys) == sorted(expected_keys), \
                f"Expected: {sorted(expected_keys)} but got: {sorted(actual_keys)}"

        assert response.status_code == expected_status_code, f"UNEXPECTED RESPONSE {response.status_code}: " \
                                                             f"{response.text}"
        return True

    def check_status_code(self, response: requests.Response, expected_status_code: int) -> bool:
        """Compare the actual and expected status code for a given response"""
        self._validate_response(response)
        self._verify_status_code(expected_status_code)
        return response.status_code == expected_status_code

    def check_and_return_endpoint(
        self,
        verb: str,
        endpoint: str,
        expected_status_code: int,
        expected_response: Union[dict, str, list],
        **kwargs,
    ) -> requests.Response:
        """Check a given request is returning the expected values. Return the response outcome"""
        response = self.get_response(verb, endpoint, **kwargs)
        assert self._verify_response(response, expected_status_code, expected_response, **kwargs)
        return response

    def check_redirect(self,
                       response: dict,
                       expected_params: dict,
                       client_redirect: str = None,
                       state: str = None):
        redirected_url = response['headers']["Location"]
        params = self.get_params_from_url(redirected_url)
        if state:
            expected_params["state"] = str(state)
        assert self.check_params(params, expected_params), (
            f"Expected: {expected_params}, but got: {params}"
        )
        if client_redirect:
            assert redirected_url.startswith(client_redirect)

    def check_endpoint(
        self,
        verb: str,
        endpoint: str,
        expected_status_code: int,
        expected_response: Union[dict, str, list],
        **kwargs,
    ) -> bool:
        """Check a given request is returning the expected values. Return the verification outcome"""
        response = self.get_response(verb, endpoint, **kwargs)
        return self._verify_response(response, expected_status_code, expected_response, **kwargs)

    def _verify_response(
        self,
        response,
        expected_status_code,
        expected_response,
        **kwargs
    ) -> bool:
        """Check a given request is returning the expected values. NOTE the expected response can be either a dict,
        a string or a list this is because we can expect either json, html, str or a list of keys from a json response
        respectively."""
        if type(expected_response) is list:
            assert self.verify_response_keys(response, expected_status_code, expected_keys=expected_response), \
                f"UNEXPECTED RESPONSE {response.status_code}: {response.text}"  # type: ignore
            return True

        # Check response
        redirected = kwargs["allow_redirects"] if "allow_redirects" in kwargs else True
        assert self._verify_response_content(
            response,
            expected_status_code,
            expected_response=expected_response,
            redirected=redirected
        ), \
            f"UNEXPECTED RESPONSE {response.status_code}: {response.text}"  # type: ignore
        return True

    def check_response_history(self, verb: str, endpoint: str, expected_redirects: dict, **kwargs) -> bool:
        """Check the response redirects for a given request is returning the expected values"""
        response = self.get_response(verb, endpoint, **kwargs)
        actual_redirects = self.get_redirects(response)

        for actual, expected in zip(
            actual_redirects.values(), expected_redirects.values()
        ):
            url = self.remove_param_from_url(actual["url"], "state")
            location = self.remove_param_from_url(
                actual["headers"]["Location"], "state"
            )

            assert (
                actual["status_code"] == expected["status_code"]
            ), f"Redirect failed with {expected['status_code']}"
            assert url == expected["url"], "Redirect url not as expected"
            assert (
                location == expected["headers"]["Location"]
            ), "Location header not as expected"
        return True

    def _verify_response_content(
        self,
        response: requests.Response,
        expected_status_code: int,
        expected_response: Union[dict, str],
        redirected: bool,
    ) -> bool:
        """Check a given response has returned the expected key value pairs"""

        assert self.check_status_code(response, expected_status_code), \
            f'UNEXPECTED RESPONSE {response.status_code}: {response.text}'

        if not redirected:
            assert (
                expected_response == response.text
            ), f'UNEXPECTED RESPONSE {response.status_code}: {response.text}'
            return True

        try:
            data = loads(response.text)
            # Strip out white spaces
            actual_response = dict(
                (
                    k.strip().lower() if isinstance(k, str) else k,
                    v.strip().lower() if isinstance(v, str) else v,
                )
                for k, v in data.items()
            )
            actual_response.pop('message_id', None)
            assert actual_response == expected_response, f"Expected: {expected_response} but got: {actual_response}"
        except JSONDecodeError:
            # Might be HTML
            # We need to get rid of the dynamic state here so we can compare the text to the stored value
            actual_response = sub('<input name="state" type="hidden" value="[a-zA-Z0-9_-]{36}">', "", response.text)

            assert actual_response.replace("\n", "").replace(" ", "").strip() == expected_response.replace(
                "\n", "").replace(" ", "").strip(), f"UNEXPECTED RESPONSE: {actual_response}"

        return True

    def has_header(self, response: requests.Response, header_key: str) -> bool:
        """Confirm if a header exists in the provided response"""
        self._validate_response(response)
        headers = [header.lower() for header in response.headers.keys()]
        return header_key.lower() in headers

    @staticmethod
    def get_headers(response: requests.Response) -> dict:
        return dict(response.headers.items())

    @staticmethod
    def get_params_from_url(url: str) -> dict:
        """Returns all the params and param values from a given url as a dictionary"""
        return dict(parse.parse_qsl(parse.urlsplit(url).query))

    def get_param_from_url(self, url: str, param: str) -> str:
        """Returns a single param and its value as a dictionary"""
        params = self.get_params_from_url(url)
        return params[param]

    def get_all_values_from_json_response(self, response: requests.Response) -> dict:
        """Convert json response string into a python dictionary"""
        self._validate_response(response)
        return loads(response.text)

    def get_value_from_json_response(self, response: requests.Response, key: str) -> str:
        """Returns the content of the response, in unicode"""
        data = self.get_all_values_from_json_response(response)
        try:
            return data[key]
        except KeyError:
            raise Exception(f"Value: {key} not found in response")

    @staticmethod
    def remove_param_from_url(url: str, param_to_remove: str) -> str:
        """This method will remove a given param from a url
        and reconstruct the url before returning it to the user"""
        url, query = url.split("?")
        params = query.split("&")

        for i, param in enumerate(params):
            if param.startswith(param_to_remove):
                continue
            if i == 0:
                url += f"?{param}"
            elif param.startswith("goto"):
                key, val = param.split("=")
                # Assuming state is the last param in the goto value url
                # which seems to be the case in all the testing done so far.
                url += f'&{key}={val[:val.index("%26state")]}'
            else:
                url += f"&{param}"
        return url

    @staticmethod
    def convert_dict_into_params(obj: dict) -> Optional[str]:
        """Takes a dictionary and converts it into url parameters
        e.g. the input: {'a':'A', 'b':'B'} will create the output: 'a=A&b=B'"""
        if obj:
            return urlencode(obj)
