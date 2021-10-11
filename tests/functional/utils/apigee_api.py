import json
import uuid
import base64
import requests

from tests.functional.config_files.config import APIGEE_TOKEN, APIGEE_API_URL, ENVIRONMENT


class ApigeeDebugApi:
    def __init__(self, proxy: str):
        super(ApigeeDebugApi, self).__init__()
        self.session_name = self._generate_uuid()
        self.proxy = proxy
        self.session = requests.Session()

        # if APIGEE_USERNAME != '' and APIGEE_PASSWORD != '':
        #     token = base64.b64encode(f'{APIGEE_USERNAME}:{APIGEE_PASSWORD}'.encode('ascii'))
        #     self.headers = {'Authorization': f'Basic {token.decode("ascii")}'}
        # elif APIGEE_AUTHENTICATION != '':
        self.headers = {'Authorization': f'Bearer {APIGEE_TOKEN}'}

        # else:
        #     raise Exception("None of apigee authentication methods is provided. If you're running this remotely you \
        #         must provide APIGEE_AUTHENTICATION otherwise provide APIGEE_USERNAME and APIGEE_PASSWORD")

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
        url = f"{APIGEE_API_URL}/environments/{ENVIRONMENT}/apis/{self.proxy}/revisions/{self.revision}/" \
              f"debugsessions?session={self.session_name}&header_X-Request-ID={request_id}"

        response = self.session.post(url, headers=self.headers)

        if response.status_code != 201:
            raise ValueError(f"Unable to create apigee debug session {self.session_name}")

    def _get_transaction_id(self) -> str:
        url = f"{APIGEE_API_URL}/environments/{ENVIRONMENT}/apis/{self.proxy}/revisions/{self.revision}/" \
              f"debugsessions/{self.session_name}/data"

        response = self.session.get(url, headers=self.headers)

        if response.status_code != 200:
            raise ValueError(f"Unable to get apigee transaction id for {self.session_name}")

        return response.text.strip('[]').replace("\"", "").strip().split(', ')[2]

    def _get_transaction_data(self) -> dict:
        transaction_id = self._get_transaction_id()
        url = f"{APIGEE_API_URL}/environments/{ENVIRONMENT}/apis/{self.proxy}/revisions/{self.revision}/" \
              f"debugsessions/{self.session_name}/data/{transaction_id}"

        response = self.session.get(url, headers=self.headers)

        if response.status_code != 200:
            raise ValueError(f"Unable to get apigee transaction {transaction_id}")

        return json.loads(response.text)

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
        executions = [x.get('results', None) for x in data['point'] if x.get('id', "") == "Execution"]
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

    def dump_data(self):
        data = self._get_transaction_data()
        print(json.dumps(data))

