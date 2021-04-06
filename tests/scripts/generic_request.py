import requests
from json import loads, JSONDecodeError
from urllib import parse
from re import sub
from urllib.parse import urlparse, urlencode
from typing import Optional
from typing import Union, Generic, TypeVar


class GenericRequest:
    """This is a base class to facilitate testing an API.
    It contains reusable components & functions that can be shared between different APIs"""

    def __init__(self):
        self.session = requests.Session()

    def get_response(self, verb: str, url: str, **kwargs) -> requests.Response:
        """Verify the arguments and then send a request and return the response.

        Params:
            verb (str): The HTTP method.
            url (str): The endpoint url.

        Returns:
            response (requests.Response): HTTP response.

        """
        if not self.is_url(url):
            raise RuntimeError("Endpoint not found")

        request_types = {
            'post': self.post,
            'get': self.get,
            'put': self.put,
            'patch': self.patch
        }

        # Verify http verb is valid
        if verb.lower() not in request_types:
            raise RuntimeError(f"Verb: {verb} is invalid")

        # Determines the request method
        func = request_types[verb.lower()]

        # Get response
        return func(url, **kwargs)

    @staticmethod
    def check_response(
        resp: requests.Response,
        expected_status_code: int,
        expected_response: Generic[TypeVar('T')],
        headers=None,
        redirects=None
    ) -> bool:
        """Reusable test step to check the result of a request.

        Args:
            resp (requests.Response): HTTP response.
            expected_status_code (int): HTTP response status code.
            expected_response (Generic[T]): Expected API response.

        Returns:
            bool: Returns the result of tests. 
        """
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
    def is_url(url: str) -> bool:
        """Check if a string looks like a URL.

        Args:
            url (str): The url to be checked.

        Returns:
            bool: Pass / Fail for url check.
        """
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False

    @staticmethod
    def _validate_response(response: requests.Response) -> None:
        """Type check response type is Response.
        Verifies the response provided is of a valid response type.

        Args:
            response (requests.Response): HTTP response.

        """
        if not type(response) == requests.models.Response:
            raise TypeError("Expected response type object for response argument")

    @staticmethod
    def check_params(params, expected_params) -> bool:
        """Checks if params dict is the same as expected params dict.

        Args:
            params (dict): HTTP params.
            expected_params (dict): HTTP params.

        Returns:
            bool: Returns true if all parameters k/v are equivalent.
        """
        return all(params.get(key) and params[key] == value for key, value in expected_params.items())

    def verify_params_exist_in_url(self, params: list, url: str) -> bool:
        """Checks if the params exist in the url.

        Args:
            params (list): A list of params to check.
            url (str): The url to parse params from.

        Returns:
            bool: Returns true if the url includes the parameters provided.
        """
        _params = self.get_params_from_url(url)
        for param in params:
            if not _params[param]:
                return False
        return True

    @staticmethod
    def _verify_status_code(status_code: Union[int, str]) -> None:
        """Verifies the status code provided is a valid status code.

        Args:
            status_code (Union[int, str]): HTTP valid status code.
        """
        if not type(status_code) == int:
            try:
                int(status_code)
            except ValueError:
                raise TypeError("Status code must only consist of numbers")
        else:
            if len(str(status_code)) != 3:
                raise TypeError("Status code must be a 3 digit number")

    def get(self, url: str, **kwargs) -> requests.Response:
        """Sends a get request and returns the response.

        Args:
            url (str): Endpoint url.

        Returns:
            response (requests.Response): HTTP Response.
        """
        try:
            return self.session.get(url, **kwargs)
        except requests.ConnectionError as e:
            raise(e)

    def post(self, url: str, **kwargs) -> requests.Response:
        """Sends a post request and returns the response.

        Args:
            url (str): Endpoint url.

        Returns:
            response (requests.Response): HTTP Response."""
        try:
            return self.session.post(url, **kwargs)
        except requests.ConnectionError as e:
            raise(e)

    def put(self, url: str, **kwargs) -> requests.Response:
        """Sends a put request and returns the response.

        Args:
            url (str): Endpoint url.

        Returns:
            response (requests.Response): HTTP Response."""
        try:
            return self.session.put(url, **kwargs)
        except requests.ConnectionError as e:
            raise(e)

    def patch(self, url: str, **kwargs) -> requests.Response:
        """Sends a patch request and returns the response.

        Args:
            url (str): Endpoint url.

        Returns:
            response (requests.Response): HTTP Response."""
        try:
            return self.session.patch(url, **kwargs)
        except requests.ConnectionError as e:
            raise(e)

    def verify_response_keys(self, response: requests.Response, expected_status_code: int,
                             expected_keys: list) -> bool:
        """Check a given response is returning the correct keys.
        In case the content is dynamic we can only check the keys and not the values.

        Args:
            response (requests.Response): HTTP Response.
            expected_status_code (int): HTTP status code.
            expected_keys (list): List of keys to check.

        Returns:
            bool: Returns true if all expected keys in the response
        """
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
        """Compare the actual and expected status code for a given response.

        Args:
            response (requests.Response): HTTP Response.
            expected_status_code (int): HTTP status code.

        Returns:
            bool: Returns the result of the endpoint.
        """
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
        """Check a given request is returning the expected values. Return the response outcome.

         Args:
            verb (str): HTTP Method.
            endpoint (str): Request endpoint.
            expected_status_code (int): HTTP status code.
            expected_response (Union[dict, str, list]): The stub to check against.

        Returns:
            response: HTTP Response.
        """
        response = self.get_response(verb, endpoint, **kwargs)
        assert self._verify_response(response, expected_status_code, expected_response, **kwargs)
        return response

    def check_redirect(self,
                       response: dict,
                       expected_params: dict,
                       client_redirect: str = None,
                       state: str = None):
        """Checks the url of the redirect.

        Args:
            response (dict): HTTP Response as dict.
            expected_params (dict): The k/v of params.
            client_redirect (str = None): The url to check the redirect url against.
            state (str = None): State string from login form.
        """
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
        """Check a given request is returning the expected values. Return the verification outcome.

        Args:
            verb (str): HTTP Method.
            endpoint (str): Request endpoint.
            expected_status_code (int): HTTP status code.
            expected_response (Union[dict, str, list]): The stub to check against.

        Returns:
            bool: Returns the result of the endpoint.
        """
        response = self.get_response(verb, endpoint, **kwargs)
        return self._verify_response(response, expected_status_code, expected_response, **kwargs)

    def _verify_response(
        self,
        response: requests.Response,
        expected_status_code: int,
        expected_response: Union[dict, str, list],
        **kwargs
    ) -> bool:
        """Check a given request is returning the expected values. NOTE the expected response can be either a dict,
        a string or a list this is because we can expect either json, html, str or a list of keys from a json response
        respectively.

        Args:
            response (requests.Response): HTTP Response.
            expected_status_code (int): HTTP status code.
            expected_response (Union[dict, str]): The stub to check against.

        Returns:
            bool: Returns the result of testing status code and response message.
        """
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

    def _verify_response_content(
        self,
        response: requests.Response,
        expected_status_code: int,
        expected_response: Union[dict, str],
        redirected: bool,
    ) -> bool:
        """Check a given response has returned the expected key value pairs.

        Args:
            response (requests.Response): HTTP Response.
            expected_status_code (int): HTTP status code.
            expected_response (Union[dict, str): The stub to check against.

        Returns:
            bool: Returns the result of testing status code and response message.
        """

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
        """Confirm if a header exists in the provided response.

        Args:
            response (requests.Response): HTTP Response.
            header_key (str): The header string to check response headers against.

        Returns:
            bool: Returns true if the header is in response.
        """
        self._validate_response(response)
        headers = [header.lower() for header in response.headers.keys()]
        return header_key.lower() in headers

    @staticmethod
    def get_headers(response: requests.Response) -> dict:
        """Converts response headers into dict.

        Args:
            response (requests.Response): HTTP Response.

        Returns:
            dict: Returns the k/v of HTTP headers.
        """
        return dict(response.headers.items())

    @staticmethod
    def get_params_from_url(url: str) -> dict:
        """Returns all the params and param values from a given url as a dictionary.

        Args:
            url (str): The url to parse params from.

        Returns:
            dict: Returns the k/v of params e.g. the input: 'input_url?a=A&b=B' will return {'a':'A', 'b':'B'}.
        """
        return dict(parse.parse_qsl(parse.urlsplit(url).query))

    def get_param_from_url(self, url: str, param: str) -> str:
        """Returns a single param and its value as a dictionary.

        Args:
            url (str): The url to parse params from.
            param (str): Value to index into dictionary of parameters.

        Returns:
            str: Returns the param value.
        """
        params = self.get_params_from_url(url)
        return params[param]

    def get_all_values_from_json_response(self, response: requests.Response) -> dict:
        """Convert json response string into a python dictionary.

        Args:
            response (requests.Response): HTTP Response.

        Returns:
            dict: Returns python dict.
        """
        self._validate_response(response)
        return loads(response.text)

    def get_value_from_json_response(self, response: requests.Response, key: str) -> str:
        """Returns the content of the response, in unicode.

        Args:
            response (requests.Response): HTTP Response.
            key (str): The key to index into a JSON Response.

        Returns:
            str: The JSON Response value indexed by key.
        """
        data = self.get_all_values_from_json_response(response)
        try:
            return data[key]
        except KeyError:
            raise Exception(f"Value: {key} not found in response")

    @staticmethod
    def convert_dict_into_params(obj: dict) -> Optional[str]:
        """Takes a dictionary and converts it into url parameters
        e.g. the input: {'a':'A', 'b':'B'} will create the output: 'a=A&b=B'.

        Args:
            obj (dict): The k/v's to be convert into url params.
        """
        if obj:
            return urlencode(obj)
