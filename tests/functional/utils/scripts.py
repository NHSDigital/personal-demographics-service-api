from ..config_files import config
import requests
import json
from pytest_check import check
import urllib.parse


class PDS:
    def __init__(self):
        super(PDS, self).__init__()

    @staticmethod
    # A function to send a PDS Retrieve request. Arguments accepted are the Patient_ID & Header.
    def retrieve_patient(patient, headers={}):
        response = requests.get(f"{config.PDS_BASE_PATH}/Patient/{patient}", headers=headers)
        return response

    @staticmethod
    # A function to send a PDS Retrieve request. Arguments accepted are the Query Parameters & Header.
    def search_patient(query_params, headers={}):
        #  check whether the query_params have been sent as a dictionary or string
        if type(query_params) == str:
            params = query_params
        else:
            params = PDS.convert_dict_into_params(query_params)
        response = requests.get(f"{config.PDS_BASE_PATH}/Patient?{params}", headers=headers)
        return response

    @staticmethod
    # A function to send a PDS Update request.  Argument accepted are Patient_ID, Patients record version,
    # Patch Payload, and any additional Headers.
    def update_patient(patient, patient_record, payload, extra_headers={}):
        headers = {"Content-Type": "application/json-patch+json", "If-Match": f'W/"{patient_record}"'}
        headers.update(extra_headers)
        response = requests.patch(f"{config.PDS_BASE_PATH}/Patient/{patient}", headers=headers, json=payload)
        return response

    @staticmethod
    # A function to send a PDS Update request where the standard headers need to be amended.
    # Argument accepted are Patient_ID, Patch Payload, and any additional Headers.
    def update_patient_invalid_headers(patient, payload, headers=None):
        response = requests.patch(f"{config.PDS_BASE_PATH}/Patient/{patient}", headers=headers, json=payload)
        return response

    @staticmethod
    # A function to send a PDS Retrieve Related Person request. Arguments accepted are the Patient_ID & Header.
    def retrieve_related_person(patient, headers={}):
        response = requests.get(f"{config.PDS_BASE_PATH}/Patient/{patient}/RelatedPerson", headers=headers)
        return response

    @staticmethod
    def poll_message(content_location):
        response = requests.get(f"{config.PDS_BASE_PATH}{content_location}")
        return response

    @staticmethod
    #  A Function to check the Response Body of a Retrieve or Polling Request.
    #  Arguments accepted are the actual Response & expected Response.
    def check_retrieve_response_body(response, expected_response):
        response_body = json.loads(response.text)
        with check:
            assert response_body == expected_response, f"UNEXPECTED RESPONSE: " \
                                                       f"actual response_body is: {response_body}" \
                                                       f"expected response_body is: {expected_response}"

    @staticmethod
    #  A Function to check the Response Body of an Update Request.
    #  Arguments accepted are the actual Response & expected Response.
    def check_update_response_body(response, expected_response):
        if response.text == "":
            response_body = ""
        else:
            response_body = json.loads(response.text)
        with check:
            assert response_body == expected_response, f"UNEXPECTED RESPONSE: " \
                                                       f"actual response_body is: {response_body}" \
                                                       f"expected response_body is: {expected_response}"

    @staticmethod
    #  A Function to check the Response Body of a Search & RelatedPerson Request.
    #  Arguments accepted are the actual Response & expected Response.
    def check_search_response_body(response, expected_response):
        response_body = PDS.remove_time_stamp_on_search_response(json.loads(response.text))
        with check:
            assert response_body == expected_response, f"UNEXPECTED RESPONSE: " \
                                                       f"actual response_body is: {response_body}" \
                                                       f"expected response_body is: {expected_response}"

    @staticmethod
    #  A Function to check the Response Status Code of a response.  Arguments accepted are the
    #  actual Response & expected Response.
    def check_response_status_code(response, expected_status):
        with check:
            assert response.status_code == expected_status, \
                f"UNEXPECTED RESPONSE: " \
                f"actual response_status is: {response.status_code} " \
                f"expected response_status is: {expected_status}"

    @staticmethod
    #  A Function to check the Response Headers.  Arguments accepted are the actual Response & expected Response.
    def check_response_headers(response, expected_headers={}):
        if 'X-Request-ID' in expected_headers:
            with check:
                assert response.headers['X-Request-ID'] == expected_headers['X-Request-ID'], \
                    f"UNEXPECTED RESPONSE: " \
                    f"actual X-Request-ID is: {response.headers['X-Request-ID']} " \
                    f"expected X-Request-ID is: {expected_headers['X-Request-ID']}"
        else:
            with check:
                assert 'X-Request-ID' not in response.headers, \
                    f"UNEXPECTED RESPONSE: expected X-Request-ID not to be present " \
                    f"but {response.headers['X-Request-ID']} found in response header"

        if 'X-Correlation-ID' in expected_headers:
            with check:
                assert response.headers['X-Correlation-ID'] == expected_headers[
                    'X-Correlation-ID'], f"UNEXPECTED RESPONSE: " \
                                         f"actual X-Request-ID is: {response.headers['X-Correlation-ID']} " \
                                         f"expected X-Request-ID is: {expected_headers['X-Correlation-ID']}"

        else:
            with check:
                assert 'X-Correlation-ID' not in response.headers, \
                    f"UNEXPECTED RESPONSE: expected X-Correlation-ID not to be present " \
                    f"but {response.headers['X-Correlation-ID']} found in response header"

    @staticmethod
    def remove_time_stamp_on_search_response(response_body):
        if "timestamp" in response_body:
            response_body.pop("timestamp")
        return response_body

    @staticmethod
    def convert_dict_into_params(obj: dict):
        """Takes a dictionary and converts it into url parameters
        e.g. the input: {'a':'A', 'b':'B'} will create the output: 'a=A&b=B'"""
        if obj:
            return urllib.parse.urlencode(obj)
