from tests.scripts.generic_request import GenericRequest
from json import loads, JSONDecodeError
from uuid import uuid4
from requests import Response
from . import config


class PdsRecord:
    """This class turns a PDS response into a object."""

    def __init__(self, response: Response):

        if type(response) is dict:
            self.response = response
        else:
            self.status_code = response.status_code
            self.headers = dict(response.headers.items())
            self.redirects = self._get_redirects(response)
            self.url = response.url
            try:
                self.response = loads(response.text)
            except JSONDecodeError as e:
                print(f'UNEXPECTED RESPONSE: {response.text}. \n Error: {e}')
                self.response = {}
                # raise Exception(f'UNEXPECTED RESPONSE: {response.text}. \n Error: {e}')

        # if the response is a list of entries i.e. a response from a search
        if 'entry' in self.response:
            self.records = [PdsRecord(entry) for entry in self.response.get('entry')]

        # if response is an error
        elif "issue" in self.response:
            self.error = self._parse_error(self.response)

        # if it is not a search or an error then it must be a single retrieve
        else:
            self._construct(self.response)

    @property
    def is_sensitive(self):
        """Stored boolean to identify if patient record is considered sensitive"""
        security = getattr(self, 'security', None)
        if security:
            return (False, True)[security[0]['code'].lower() == 'r' and security[0]['display'].lower() == 'restricted']

    def _construct(self, obj: dict):
        """A recursive method for setting attributes to the instance from a given dictionary"""
        for k, v in obj.items():
            if isinstance(v, dict):
                setattr(self, k, self._construct(v))
            else:
                setattr(self, k, v)

    @staticmethod
    def _get_redirects(response: Response) -> dict:
        redirects = {}
        if response.history:
            for i, resp in enumerate(response.history):
                redirects[i] = {'status_code': resp.status_code, 'url': resp.url, 'headers': resp.headers}
        return redirects

    @staticmethod
    def _parse_error(response: dict) -> dict:
        return {response['resourceType']: response['issue'][0]}

    def _get_error_resource_type(self) -> dict:
        return self.response['resourceType']

    def check_error(self, expected_status_code: int, expected_error_message: str) -> bool:
        if not self.error['status_code'] == expected_status_code:
            return False
        if not self.error['details']['display'] == expected_error_message:
            return False
        return True

    def get_extension_by_url(self, url_contains: str) -> dict:
        """This will return the first match it find."""
        for extension in getattr(self, "extension", {}):
            if url_contains.lower() in extension.get('url', '').lower():
                return extension
            for ext in extension.get('extension', {}):
                if url_contains.lower() in ext.get('url', '').lower():
                    return ext

    def get_consolidated_error(self):
        """Returns a simplified and cleaner version of the error response"""
        details = self.error[self._get_error_resource_type()]['details']['coding'][0]
        details['diagnostics'] = self.error[self._get_error_resource_type()]['diagnostics']
        details['error_resource_type'] = self._get_error_resource_type()
        details['status_code'] = self.status_code
        return details


class GenericPdsRequestor(GenericRequest):
    """A utility class to make generic PDS requests. """

    def __init__(
        self,
        pds_base_path: str,
        base_url: str,
        token: str = None,
        headers: dict = None
    ):
        super(GenericPdsRequestor, self).__init__()
        self.base_url = f'{base_url}/{pds_base_path}'

        if headers:
            self._headers = headers
        else:
            self._headers = {
                'Authorization': f'Bearer {token}',
                'NHSD-Session-URID': config.ROLE_ID,
                'X-Request-ID': str(uuid4()),
            }

    @property
    def headers(self):
        return self._headers

    @headers.setter
    def headers(self, headers: dict):
        self._headers.update(headers)

    def get_patient_response(self, patient_id: str, **kwargs) -> PdsRecord:
        """Return a PDS record as an object"""
        response = self.get(f'{self.base_url}/Patient/{patient_id}', headers=self._headers, ** kwargs)
        return PdsRecord(response)

    def update_patient_response(self, patient_id: str, payload: dict, **kwargs) -> PdsRecord:
        """Sends a patch request and returns a PDS record as an object.

        Args:
            patient_id (str): Patient to update.
            payload: A JSON patch. E.g:
                {
                    "patches": [
                        { "op": "add", "path": "/deceasedDate", "value": "2020-01-01" }
                    ]
                }
            See for more details:
        https://digital.nhs.uk/developer/api-catalogue/personal-demographics-service-fhir#api-Default-updatePatientPartial.

        Returns:
            response (PdsRecord): PDS Record object."""
        response = self.patch(
            f'{self.base_url}/Patient/{patient_id}',
            headers=self._headers,
            json=payload,
            **kwargs
        )

        return PdsRecord(response)
