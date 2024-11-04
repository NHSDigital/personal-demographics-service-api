import pytest
from pytest_check import check
from aiohttp import ClientResponse
from .data.scenarios import relatedPerson, retrieve, search_success, search_error, invalid_headers, update
import requests
from typing import Dict
from .utils import helpers
from .configuration import config


# @pytest.mark.deployment_scenarios
# @pytest.mark.skipif(
#     config.SANDBOX_BASE_URL.startswith("http://0.0.0.0"),
#     reason="Only run these these tests against a deployed sandbox")
# class TestPDSSandboxDeploymentSuite:
#     """Sandbox PDS Deployment Scenarios. Checks performed: status_codes and version deployed"""

#     @pytest.mark.asyncio
#     async def test_wait_for_ping(self,
#                                  commit_id: str):
#         async def apigee_deployed(response: ClientResponse):
#             if response.status != 200:
#                 return False
#             body = await response.json(content_type=None)
#             return body.get("commitId") == commit_id

#         await helpers.poll_until(url=f"{config.SANDBOX_BASE_URL}/_ping",
#                                  until=apigee_deployed,
#                                  timeout=30)

#     @pytest.mark.asyncio
#     async def test_check_status_is_secured(self):
#         response = requests.get(f"{config.SANDBOX_BASE_URL}/_status")
#         assert response.status_code == 401

#     @pytest.mark.asyncio
#     async def test_wait_for_status(self,
#                                    commit_id: str,
#                                    status_endpoint_header: Dict[str, str]):
#         async def is_deployed(response: ClientResponse):
#             if response.status != 200:
#                 return False
#             body = await response.json()

#             if body.get("commitId") != commit_id:
#                 return False

#             backend = helpers.dict_path(body, path=["checks", "healthcheck", "outcome", "version"])
#             if not backend:
#                 return True

#             return backend.get("commitId") == commit_id

#         await helpers.poll_until(url=f"{config.SANDBOX_BASE_URL}/_status",
#                                  headers=status_endpoint_header,
#                                  until=is_deployed,
#                                  timeout=120)


@pytest.mark.retrieve_scenarios
class TestPDSSandboxRetrieveSuite:
    """Sandbox PDS Retrieve Scenarios. Checks performed: canned Response_Bodies, Status_Codes and Headers"""

    @pytest.mark.parametrize("scenario", retrieve.keys())
    def test_retrieve_scenarios(self, scenario, additional_headers):
        response = helpers.retrieve_patient(retrieve[scenario]["patient"], additional_headers)
        helpers.check_retrieve_response_body(response, retrieve[scenario]["response"])
        helpers.check_response_status_code(response, retrieve[scenario]["status"])
        helpers.check_response_headers(response, additional_headers)


@pytest.mark.search_scenarios
class TestPDSSandboxSearchSuite:
    @pytest.mark.parametrize("scenario", search_success.keys())
    def test_success_scenarios(self, scenario, additional_headers):
        response = helpers.search_patient(search_success[scenario]["query_params"], additional_headers)
        helpers.check_search_response_body(response, search_success[scenario]["response"])
        helpers.check_response_status_code(response, 200)
        helpers.check_response_headers(response, additional_headers)

    @pytest.mark.parametrize("scenario", search_error.keys())
    def test_error_scenarios(self, scenario, additional_headers):
        response = helpers.search_patient(search_error[scenario]["query_params"], additional_headers)
        assert response.json() == search_error[scenario]["response"]
        helpers.check_search_response_body(response, search_error[scenario]["response"])
        helpers.check_response_status_code(response, 400)
        helpers.check_response_headers(response, additional_headers)


class TestPDSSandboxInvalidHeaders:
    @pytest.mark.parametrize("parameterized_headers", [
        {},
        {"Prefer": "response-async"}
    ])
    def test_search_missing_x_request_id(self, parameterized_headers):
        scenario = "Missing X-Request-ID (search)"
        response = helpers.search_patient(invalid_headers[scenario]["query_params"], parameterized_headers)
        helpers.check_search_response_body(response, invalid_headers[scenario]["response"])
        helpers.check_response_status_code(response, 400)

    def test_invalid_x_request_id(self):
        scenario = "Invalid X-Request-ID (retrieve)"
        response = helpers.retrieve_patient(
            invalid_headers[scenario]["patient"], {"x-request-id": "1234"}
        )
        helpers.check_retrieve_response_body(response, invalid_headers[scenario]["response"])
        helpers.check_response_status_code(response, 400)
        helpers.check_response_headers(response, {"X-Request-ID": "1234"})

    @pytest.mark.parametrize('parameterized_headers', [
        {},
        {"Prefer": "respond-async"}
    ])
    def test_missing_x_request_id(self, parameterized_headers):
        scenario = "Missing X-Request-ID (retrieve)"
        response = helpers.retrieve_patient(invalid_headers[scenario]["patient"], parameterized_headers)
        helpers.check_retrieve_response_body(response, invalid_headers[scenario]["response"])
        helpers.check_response_status_code(response, 400)


@pytest.mark.update_scenarios
class TestPDSSandboxUpdateSyncWrapSuite:
    """Sandbox PDS Update Sync-Wrap Scenarios. Checks performed: canned Response_Bodies, Status_Codes and Headers"""
    def test_update_add_name(self, additional_headers):
        # Prefer header deprecated, check that header is ignored
        additional_headers["Prefer"] = "respond-async"
        # send update request
        update_response = helpers.update_patient(
            update[0]["patient"],
            update[0]["patient_record"],
            update[0]["patch"],
            additional_headers
        )
        helpers.check_retrieve_response_body(
            update_response, update[0]["response"]
        )
        helpers.check_response_status_code(update_response, 200)
        helpers.check_response_headers(update_response, additional_headers)

    def test_update_replace_given_name(self, additional_headers):
        # send update request
        update_response = helpers.update_patient(
            update[1]["patient"],
            update[1]["patient_record"],
            update[1]["patch"],
            additional_headers,
        )

        helpers.check_response_headers(update_response, additional_headers)
        helpers.check_retrieve_response_body(
            update_response, update[1]["response"]
        )
        helpers.check_response_status_code(update_response, 200)
        helpers.check_response_headers(update_response, additional_headers)

    def test_remove_suffix_from_name(self, additional_headers):
        # Prefer header deprecated, check that header is ignored
        additional_headers["Prefer"] = "respond-async"
        # send update request
        update_response = helpers.update_patient(
            update[2]["patient"],
            update[2]["patient_record"],
            update[2]["patch"],
            additional_headers,
        )

        helpers.check_retrieve_response_body(
            update_response, update[2]["response"]
        )
        helpers.check_response_status_code(update_response, 200)
        helpers.check_response_headers(update_response, additional_headers)


@pytest.mark.update_scenarios
class TestSandboxUpdateFailureSuite:
    """Sandbox PDS Update Sad Path Scenarios. Checks performed: canned Response_Bodies, Status_Codes and Headers"""

    @pytest.mark.parametrize("additional_headers", [
        dict(prefer=False),
        dict(prefer=True)],
        indirect=["additional_headers"]
    )
    def test_update_no_patch_sent(self, set_delay, additional_headers):
        # send update request
        update_response = helpers.update_patient(
            update[3]["patient"],
            update[3]["patient_record"],
            update[3]["patch"],
            additional_headers,
        )
        helpers.check_update_response_body(update_response, update[3]["response"])
        helpers.check_response_status_code(update_response, 400)
        helpers.check_response_headers(update_response, additional_headers)

    @pytest.mark.parametrize("additional_headers", [
        dict(prefer=False),
        dict(prefer=True)],
        indirect=["additional_headers"]
    )
    def test_update_incorrect_resource_version(self, set_delay, additional_headers):
        # send update request
        update_response = helpers.update_patient(
            update[4]["patient"],
            update[4]["patient_record"],
            update[4]["patch"],
            additional_headers,
        )
        helpers.check_update_response_body(update_response, update[4]["response"])
        helpers.check_response_status_code(update_response, 412)
        helpers.check_response_headers(update_response, additional_headers)

    @pytest.mark.parametrize('parameterized_headers', [
        {"x-request-id": "12345"},
        {"x-request-id": "12345", "Prefer": "respond-async"}
    ])
    def test_update_invalid_x_request_id(self, set_delay, parameterized_headers):
        # send update request
        update_response = helpers.update_patient(
            update[5]["patient"],
            update[5]["patient_record"],
            update[5]["patch"],
            parameterized_headers,
        )
        helpers.check_update_response_body(update_response, update[5]["response"])
        helpers.check_response_status_code(update_response, 400)
        helpers.check_response_headers(update_response, {"X-Request-ID": "12345"})

    @pytest.mark.parametrize('parameterized_headers', [
        {},
        {"Prefer": "respond-async"}
    ])
    def test_update_missing_x_request_id(self, set_delay, parameterized_headers):
        # send update request
        update_response = helpers.update_patient(
            update[5]["patient"],
            update[5]["patient_record"],
            update[5]["patch"],
            parameterized_headers
        )

        helpers.check_update_response_body(update_response, update[11]["response"])
        helpers.check_response_status_code(update_response, 400)

    @pytest.mark.parametrize('parameterized_headers', [
        {"Content-Type": "application/json-patch+json"},
        {"Content-Type": "application/json-patch+json", "Prefer": "respond-async"}
    ])
    def test_update_missing_if_match_header(self, set_delay, parameterized_headers):
        update_response = helpers.update_patient_invalid_headers(
            update[6]["patient"], update[6]["patch"], parameterized_headers
        )
        helpers.check_update_response_body(update_response, update[6]["response"])
        helpers.check_response_status_code(update_response, 412)
        helpers.check_response_headers(update_response)

    @pytest.mark.parametrize('parameterized_headers', [
        {"Content-Type": "text/xml", "If-Match": 'W/"2"'},
        {"Content-Type": "text/xml", "If-Match": 'W/"2"', "Prefer": "respond-async"}
    ])
    def test_update_incorrect_content_type(self, set_delay, parameterized_headers):
        update_response = helpers.update_patient_invalid_headers(
            update[7]["patient"], update[7]["patch"], parameterized_headers
        )
        helpers.check_update_response_body(update_response, update[7]["response"])
        helpers.check_response_status_code(update_response, 400)
        helpers.check_response_headers(update_response)

    @pytest.mark.parametrize("additional_headers", [
        dict(prefer=False),
        dict(prefer=True)],
        indirect=["additional_headers"]
    )
    def test_update_invalid_patch(self, set_delay, additional_headers):
        # send update request
        update_response = helpers.update_patient(
            update[8]["patient"],
            update[8]["patient_record"],
            update[8]["patch"],
            additional_headers,
        )
        helpers.check_update_response_body(update_response, update[8]["response"])
        helpers.check_response_status_code(update_response, 400)
        helpers.check_response_headers(update_response, additional_headers)

    @pytest.mark.parametrize("additional_headers", [
        dict(prefer=False),
        dict(prefer=True)],
        indirect=["additional_headers"]
    )
    def test_invalid_nhs_number(self, set_delay, additional_headers):
        # send update request
        update_response = helpers.update_patient(
            update[9]["patient"],
            update[9]["patient_record"],
            update[9]["patch"],
            additional_headers,
        )
        helpers.check_update_response_body(update_response, update[9]["response"])
        helpers.check_response_status_code(update_response, 400)
        helpers.check_response_headers(update_response, additional_headers)

    @pytest.mark.parametrize("additional_headers", [
        dict(prefer=False),
        dict(prefer=True)],
        indirect=["additional_headers"]
    )
    def test_patient_does_not_exist(self, set_delay, additional_headers):
        # send update request
        update_response = helpers.update_patient(
            update[10]["patient"],
            update[10]["patient_record"],
            update[10]["patch"],
            additional_headers,
        )
        helpers.check_update_response_body(update_response, update[10]["response"])
        helpers.check_response_status_code(update_response, 404)
        helpers.check_response_headers(update_response, additional_headers)

    @pytest.mark.parametrize("additional_headers", [
        dict(prefer=False),
        dict(prefer=True)],
        indirect=["additional_headers"]
    )
    def test_update_invalid_patch_no_address_id(self, set_delay, additional_headers):
        # send update request
        update_response = helpers.update_patient(
            update[12]["patient"],
            update[12]["patient_record"],
            update[12]["patch"],
            additional_headers,
        )
        helpers.check_update_response_body(update_response, update[12]["response"])
        helpers.check_response_status_code(update_response, 400)
        helpers.check_response_headers(update_response, additional_headers)

    @pytest.mark.parametrize("additional_headers", [
        dict(prefer=False),
        dict(prefer=True)],
        indirect=["additional_headers"]
    )
    def test_replace_address_all_line_entries(self, set_delay, additional_headers):
        # send update request
        update_response = helpers.update_patient(
            update[13]["patient"],
            update[13]["patient_record"],
            update[13]["patch"],
            additional_headers,
        )
        helpers.check_update_response_body(update_response, update[13]["response"])
        helpers.check_response_status_code(update_response, 400)
        helpers.check_response_headers(update_response, additional_headers)

    @pytest.mark.parametrize("additional_headers", [
        dict(prefer=False),
        dict(prefer=True)],
        indirect=["additional_headers"]
    )
    def test_no_address_id(self, set_delay, additional_headers):
        # send update request
        update_response = helpers.update_patient(
            update[14]["patient"],
            update[14]["patient_record"],
            update[14]["patch"],
            additional_headers,
        )
        helpers.check_update_response_body(update_response, update[14]["response"])
        helpers.check_response_status_code(update_response, 400)
        helpers.check_response_headers(update_response, additional_headers)

    @pytest.mark.parametrize("additional_headers", [
        dict(prefer=False),
        dict(prefer=True)],
        indirect=["additional_headers"]
    )
    def test_invalid_address_id(self, set_delay, additional_headers):
        # send update request
        update_response = helpers.update_patient(
            update[15]["patient"],
            update[15]["patient_record"],
            update[15]["patch"],
            additional_headers,
        )
        helpers.check_update_response_body(update_response, update[15]["response"])
        helpers.check_response_status_code(update_response, 400)
        helpers.check_response_headers(update_response, additional_headers)

    @pytest.mark.parametrize("additional_headers", [
        dict(prefer=False),
        dict(prefer=True)],
        indirect=["additional_headers"]
    )
    def test_invalid_address_id_only(self, set_delay, additional_headers):
        # send update request
        update_response = helpers.update_patient(
            update[16]["patient"],
            update[16]["patient_record"],
            update[16]["patch"],
            additional_headers,
        )
        helpers.check_update_response_body(update_response, update[16]["response"])
        helpers.check_response_status_code(update_response, 400)
        helpers.check_response_headers(update_response, additional_headers)

    @pytest.mark.parametrize("additional_headers", [
        dict(prefer=False),
        dict(prefer=True)],
        indirect=["additional_headers"]
    )
    def test_patient_with_no_address(self, set_delay, additional_headers):
        # send update request
        update_response = helpers.update_patient(
            update[17]["patient"],
            update[17]["patient_record"],
            update[17]["patch"],
            additional_headers,
        )
        helpers.check_update_response_body(update_response, update[17]["response"])
        helpers.check_response_status_code(update_response, 400)
        helpers.check_response_headers(update_response, additional_headers)

    @pytest.mark.parametrize("additional_headers", [
        dict(prefer=False),
        dict(prefer=True)],
        indirect=["additional_headers"]
    )
    def test_patient_with_no_address_request_without_addres_id(self, set_delay, additional_headers):
        # send update request
        update_response = helpers.update_patient(
            update[18]["patient"],
            update[18]["patient_record"],
            update[18]["patch"],
            additional_headers,
        )
        helpers.check_update_response_body(update_response, update[18]["response"])
        helpers.check_response_status_code(update_response, 400)
        helpers.check_response_headers(update_response, additional_headers)


@pytest.mark.related_person_scenarios
class TestSandboxRelatedPersonSuite:
    """Sandbox PDS Related Person Scenarios. Checks performed: canned Response_Bodies, Status_Codes and Headers"""

    def test_related_person_exists(self, additional_headers):
        response = helpers.retrieve_related_person(
            relatedPerson[0]["patient"], additional_headers
        )
        helpers.check_search_response_body(response, relatedPerson[0]["response"])
        helpers.check_response_status_code(response, 200)
        helpers.check_response_headers(response, additional_headers)

    def test_related_person_patient_does_not_exist(self, additional_headers):
        response = helpers.retrieve_related_person(
            relatedPerson[1]["patient"], additional_headers
        )
        helpers.check_search_response_body(response, relatedPerson[1]["response"])
        helpers.check_response_status_code(response, 404)
        helpers.check_response_headers(response, additional_headers)

    def test_related_person_does_not_exist(self, additional_headers):
        response = helpers.retrieve_related_person(
            relatedPerson[2]["patient"], additional_headers
        )
        helpers.check_search_response_body(response, relatedPerson[2]["response"])
        helpers.check_response_status_code(response, 200)
        helpers.check_response_headers(response, additional_headers)

    def test_related_person_can_contain_empty_patient_object(self, additional_headers):
        response = helpers.retrieve_related_person("9000000017", additional_headers)
        with check:
            assert response.status_code == 200
            assert response.json()['entry'][0]['resource']['patient'] == {}
