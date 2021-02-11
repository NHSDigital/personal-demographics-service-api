from .data.pds_scenarios import retrieve, search, update
from .utils import helpers
import json
from pytest_check import check


class TestUserRestrictedRetrievePatient:

    def test_retrieve_patient(self, headers_with_token):
        response = helpers.retrieve_patient(
            retrieve[0]["patient"],
            self.headers
        )
        helpers.check_retrieve_response_body(response, retrieve[0]["response"])
        helpers.check_response_status_code(response, 200)
        helpers.check_response_headers(response, self.headers)

    def test_retrieve_patient_with_missing_auth_header(self, headers):
        response = helpers.retrieve_patient(
            retrieve[1]["patient"],
            headers
        )
        helpers.check_retrieve_response_body(response, retrieve[1]["response"])
        helpers.check_response_status_code(response, 401)
        helpers.check_response_headers(response, headers)

    def test_retrieve_patient_with_blank_auth_header(self, headers):
        headers['authorization'] = ''
        response = helpers.retrieve_patient(
            retrieve[1]["patient"],
            headers
        )
        helpers.check_retrieve_response_body(
            response,
            retrieve[1]["response"]
        )
        helpers.check_response_status_code(response, 401)
        helpers.check_response_headers(response, headers)

    def test_retrieve_patient_with_invalid_auth_header(self, headers):
        headers['authorization'] = 'Bearer abcdef123456789'
        response = helpers.retrieve_patient(
            retrieve[2]["patient"],
            headers
        )
        helpers.check_retrieve_response_body(response, retrieve[2]["response"])
        helpers.check_response_status_code(response, 401)
        helpers.check_response_headers(response, headers)

    def test_retrieve_patient_with_missing_urid_header(self, headers_with_token):
        self.headers.pop("NHSD-Session-URID")
        response = helpers.retrieve_patient(
            retrieve[3]["patient"],
            self.headers
        )
        helpers.check_retrieve_response_body(response, retrieve[3]["response"])
        helpers.check_response_status_code(response, 400)
        helpers.check_response_headers(response, self.headers)

    def test_retrieve_patient_with_blank_x_request_header(self, headers_with_token):
        self.headers["X-Request-ID"] = ''
        response = helpers.retrieve_patient(
            retrieve[4]["patient"],
            self.headers
        )
        helpers.check_retrieve_response_body(response, retrieve[4]["response"])
        helpers.check_response_status_code(response, 400)
        self.headers.pop("X-Request-ID")
        helpers.check_response_headers(response, self.headers)

    def test_retrieve_patient_with_invalid_x_request_header(self, headers_with_token):
        self.headers["X-Request-ID"] = '1234'
        response = helpers.retrieve_patient(
            retrieve[5]["patient"],
            self.headers
        )
        helpers.check_retrieve_response_body(response, retrieve[5]["response"])
        helpers.check_response_status_code(response, 400)
        helpers.check_response_headers(response, self.headers)

    def test_retrieve_patient_with_missing_x_request_header(self, headers_with_token):
        self.headers.pop("X-Request-ID")
        response = helpers.retrieve_patient(
            retrieve[6]["patient"],
            self.headers
        )
        helpers.check_retrieve_response_body(response, retrieve[6]["response"])
        helpers.check_response_status_code(response, 412)
        helpers.check_response_headers(response, self.headers)


class TestUserRestrictedSearchPatient:

    def test_search_patient_happy_path(self, headers_with_token):
        response = helpers.search_patient(
            search[0]["query_params"],
            self.headers
        )
        helpers.check_search_response_body(response, search[0]["response"])
        helpers.check_response_status_code(response, 200)
        helpers.check_response_headers(response, self.headers)

    def test_search_patient_with_missing_auth_header(self, headers):
        response = helpers.search_patient(
            search[1]["query_params"],
            headers
        )
        helpers.check_search_response_body(response, search[1]["response"])
        helpers.check_response_status_code(response, 401)
        helpers.check_response_headers(response, headers)

    def test_search_patient_with_blank_auth_header(self, headers):
        headers['authorization'] = ''
        response = helpers.search_patient(
            search[1]["query_params"],
            headers
        )
        helpers.check_search_response_body(response, search[1]["response"])
        helpers.check_response_status_code(response, 401)
        helpers.check_response_headers(response, headers)

    def test_search_patient_with_invalid_auth_header(self, headers):
        headers['authorization'] = 'Bearer abcdef123456789'
        response = helpers.search_patient(
            search[2]["query_params"],
            headers
        )
        helpers.check_search_response_body(response, search[2]["response"])
        helpers.check_response_status_code(response, 401)
        helpers.check_response_headers(response, headers)

    def test_search_patient_with_missing_urid_header(self, headers_with_token):
        self.headers.pop("NHSD-Session-URID")
        response = helpers.search_patient(
            search[3]["query_params"],
            self.headers
        )
        helpers.check_search_response_body(response, search[3]["response"])
        helpers.check_response_status_code(response, 400)
        helpers.check_response_headers(response, self.headers)

    def test_search_patient_with_blank_x_request_header(self, headers_with_token):
        self.headers["X-Request-ID"] = ''
        response = helpers.search_patient(
            search[4]["query_params"],
            self.headers
        )
        helpers.check_search_response_body(response, search[4]["response"])
        helpers.check_response_status_code(response, 400)
        self.headers.pop("X-Request-ID")
        helpers.check_response_headers(response, self.headers)

    def test_search_patient_with_invalid_x_request_header(self, headers_with_token):
        self.headers["X-Request-ID"] = '1234'
        response = helpers.search_patient(
            search[5]["query_params"],
            self.headers
        )
        helpers.check_search_response_body(response, search[5]["response"])
        helpers.check_response_status_code(response, 400)
        helpers.check_response_headers(response, self.headers)

    def test_search_patient_with_missing_x_request_header(self, headers_with_token):
        self.headers.pop("X-Request-ID")
        response = helpers.search_patient(
            search[6]["query_params"],
            self.headers
        )
        helpers.check_search_response_body(response, search[6]["response"])
        helpers.check_response_status_code(response, 412)
        helpers.check_response_headers(response, self.headers)

    def test_search_patient_happy_path_genderfree(self, headers_with_token):
        response = helpers.search_patient(
            search[7]["query_params"],
            self.headers
        )
        helpers.check_search_response_body(response, search[0]["response"])
        helpers.check_response_status_code(response, 200)
        helpers.check_response_headers(response, self.headers)


class TestUserRestrictedPatientUpdate:

    def test_update_patient_dob(self, headers_with_token, create_random_date):

        #  send retrieve patient request to retrieve the patient record (Etag Header) & versionId
        response = helpers.retrieve_patient(
            update[0]["patient"],
            self.headers
        )
        patient_record = response.headers["Etag"]
        versionId = (json.loads(response.text))["meta"]["versionId"]

        # add the new dob to the patch, send the update and check the response
        update[0]["patch"]["patches"][0]["value"] = self.new_date
        update_response = helpers.update_patient(
            update[0]["patient"],
            patient_record,
            update[0]["patch"],
            self.headers
        )
        with check:
            assert update_response.text == ""
        helpers.check_response_status_code(update_response, 202)
        helpers.check_response_headers(update_response, self.headers)

        # send message poll request and check the response contains the updated attributes
        poll_message_response = helpers.poll_message(
            update_response.headers["content-location"],
            self.headers
        )

        with check:
            assert (json.loads(poll_message_response.text))["birthDate"] == self.new_date
        with check:
            assert int((json.loads(poll_message_response.text))["meta"]["versionId"]) == int(versionId) + 1
        helpers.check_response_status_code(poll_message_response, 200)

    def test_update_patient_with_missing_auth_header(self, headers):
        update_response = helpers.update_patient(
            update[1]["patient"],
            'W/"14"',
            update[1]["patch"],
            headers
        )
        helpers.check_retrieve_response_body(update_response, update[1]["response"])
        helpers.check_response_status_code(update_response, 401)
        helpers.check_response_headers(update_response, headers)

    def test_update_patient_with_blank_auth_header(self, headers):
        headers['authorization'] = ''
        update_response = helpers.update_patient(
            update[1]["patient"],
            'W/"14"',
            update[1]["patch"],
            headers
        )
        helpers.check_retrieve_response_body(update_response, update[1]["response"])
        helpers.check_response_status_code(update_response, 401)
        helpers.check_response_headers(update_response, headers)

    def test_update_patient_with_invalid_auth_header(self, headers):
        headers['authorization'] = 'Bearer abcdef123456789'
        update_response = helpers.update_patient(
            update[2]["patient"],
            'W/"14"',
            update[2]["patch"],
            headers
        )
        helpers.check_retrieve_response_body(update_response, update[2]["response"])
        helpers.check_response_status_code(update_response, 401)
        helpers.check_response_headers(update_response, headers)

    def test_update_patient_with_missing_urid_header(self, headers_with_token):
        self.headers.pop("NHSD-Session-URID")
        update_response = helpers.update_patient(
            update[3]["patient"],
            'W/"14"',
            update[3]["patch"],
            self.headers
        )
        helpers.check_retrieve_response_body(update_response, update[3]["response"])
        helpers.check_response_status_code(update_response, 400)
        helpers.check_response_headers(update_response, self.headers)

    def test_update_patient_with_blank_x_request_header(self, headers_with_token):
        self.headers["X-Request-ID"] = ''
        update_response = helpers.update_patient(
            update[4]["patient"],
            'W/"14"',
            update[4]["patch"],
            self.headers
        )
        helpers.check_retrieve_response_body(update_response, update[4]["response"])
        helpers.check_response_status_code(update_response, 400)
        self.headers.pop("X-Request-ID")
        helpers.check_response_headers(update_response, self.headers)

    def test_update_patient_with_invalid_x_request_header(self, headers_with_token):
        self.headers["X-Request-ID"] = '1234'
        update_response = helpers.update_patient(
            update[5]["patient"],
            'W/"14"',
            update[5]["patch"],
            self.headers
        )
        helpers.check_retrieve_response_body(update_response, update[5]["response"])
        helpers.check_response_status_code(update_response, 400)
        helpers.check_response_headers(update_response, self.headers)

    def test_update_patient_with_missing_x_request_header(self, headers_with_token):
        self.headers.pop("X-Request-ID")
        update_response = helpers.update_patient(
            update[6]["patient"],
            'W/"14"',
            update[6]["patch"],
            self.headers
        )
        helpers.check_retrieve_response_body(update_response, update[6]["response"])
        helpers.check_response_status_code(update_response, 412)
        helpers.check_response_headers(update_response, self.headers)
