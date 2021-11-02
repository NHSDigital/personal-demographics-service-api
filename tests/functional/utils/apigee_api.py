import json
import uuid
import requests

from tests.functional.config_files.config import APIGEE_API_TOKEN, APIGEE_API_URL, ENVIRONMENT


class ApigeeDebugApi:
    def __init__(self, proxy: str):
        self.session_name = self._generate_uuid()
        self.proxy = proxy
        self.session = requests.Session()

        if APIGEE_API_TOKEN != '':
            self.headers = {'Authorization': f'Bearer {APIGEE_API_TOKEN}'}
        else:
            raise Exception("You must provide an apigee access token using the APIGEE_API_TOKEN runtime variable")

        self.revision = self._get_latest_revision()

    @staticmethod
    def _generate_uuid():
        unique_id = uuid.uuid4()
        return str(unique_id)

    def _get_latest_revision(self) -> str:
        url = f"{APIGEE_API_URL}/apis/{self.proxy}/revisions"

        response = self.session.get(url, headers=self.headers)
        revisions = response.json()
        return revisions[-1]

    def create_debug_session(self, request_id: str):
        """ Creates a debug session adding the given request_id as a filter, therefore only HTTP calls with that
            request-id will be captured
         """
        url = f"{APIGEE_API_URL}/environments/{ENVIRONMENT}/apis/{self.proxy}/revisions/{self.revision}/" \
              f"debugsessions?session={self.session_name}&header_x-request-id={request_id}"

        response = self.session.post(url, headers=self.headers)

        if response.status_code != 201:
            raise ValueError(f"Unable to create apigee debug session {self.session_name}")

    def _get_transaction_id(self):
        url = f"{APIGEE_API_URL}/environments/{ENVIRONMENT}/apis/{self.proxy}/revisions/{self.revision}/" \
              f"debugsessions/{self.session_name}/data"

        response = self.session.get(url, headers=self.headers)

        if response.status_code != 200:
            raise ValueError(f"Unable to get apigee transaction id for {self.session_name}")

        return response.text.strip('[]').replace("\"", "").strip().split(', ')

    def _get_transaction_data(self) -> dict:
        transaction_ids = self._get_transaction_id()
        data = []

        for transaction in transaction_ids:
            url = f"{APIGEE_API_URL}/environments/{ENVIRONMENT}/apis/{self.proxy}/revisions/{self.revision}/" \
                  f"debugsessions/{self.session_name}/data/{transaction}"

            response = self.session.get(url, headers=self.headers)

            if response.status_code != 200:
                raise ValueError(f"Unable to get apigee transaction {transaction}")

            data.append(json.loads(response.text))

        return data

    def get_apigee_variable(self, name: str) -> str:
        data = self._get_transaction_data()
        executions = [x.get('results', None) for x in data['point'] if x.get('id', "") == "Execution"]
        executions = list(filter(lambda x: x != [], executions))

        variable_accesses = []

        for execution in executions:
            for item in execution:
                if item.get('ActionResult', '') == 'VariableAccess':
                    variable_accesses.append(item)

        for result in variable_accesses:  # Configured by the application
            for item in result['accessList']:
                if item.get('Get', {}).get('name', '') == name:
                    return item.get('Get', {}).get('value', '')

    def get_apigee_header(self, name: str) -> str:
        data = self._get_transaction_data()

        for d in data:
            executions = [x.get('results', None) for x in d['point'] if x.get('id', "") == "Execution"]
            executions = list(filter(lambda x: x != [], executions))

            request_messages = []

            for execution in executions:
                for item in execution:
                    if item.get('ActionResult', '') == 'RequestMessage':
                        request_messages.append(item)

            for result in request_messages:  # One being sent as the header
                for item in result['headers']:
                    if item['name'] == name:
                        return item['value']
