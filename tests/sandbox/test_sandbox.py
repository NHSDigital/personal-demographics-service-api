import pytest
from pytest_check import check
from aiohttp import ClientResponse
from .data.scenarios import relatedPerson, retrieve, search, update
import requests
from typing import Dict
from .utils import helpers
from .configuration import config


# @pytest.mark.deployment_scenarios
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

    def test_sandbox_retrieve_patient(self, additional_headers):
        response = helpers.retrieve_patient(retrieve[0]["patient"], additional_headers)
        helpers.check_retrieve_response_body(response, retrieve[0]["response"])
        helpers.check_response_status_code(response, 200)
        helpers.check_response_headers(response, additional_headers)

    def test_patient_does_not_exist(self, additional_headers):
        response = helpers.retrieve_patient(retrieve[1]["patient"], additional_headers)
        helpers.check_retrieve_response_body(response, retrieve[1]["response"])
        helpers.check_response_status_code(response, 404)
        helpers.check_response_headers(response, additional_headers)

    def test_sensetive_patient_exists(self, additional_headers):
        response = helpers.retrieve_patient(retrieve[2]["patient"], additional_headers)
        helpers.check_retrieve_response_body(response, retrieve[2]["response"])
        helpers.check_response_status_code(response, 200)
        helpers.check_response_headers(response, additional_headers)

    def test_invalid_nhs_number(self, additional_headers):
        response = helpers.retrieve_patient(retrieve[3]["patient"], additional_headers)
        helpers.check_retrieve_response_body(response, retrieve[3]["response"])
        helpers.check_response_status_code(response, 400)
        helpers.check_response_headers(response, additional_headers)

    def test_invalid_x_request_id(self):
        response = helpers.retrieve_patient(
            retrieve[4]["patient"], {"x-request-id": "1234"}
        )
        helpers.check_retrieve_response_body(response, retrieve[4]["response"])
        helpers.check_response_status_code(response, 400)
        helpers.check_response_headers(response, {"X-Request-ID": "1234"})

    @pytest.mark.parametrize('parameterized_headers', [
        {},
        {"Prefer": "respond-async"}
    ])
    def test_missing_x_request_id(self, parameterized_headers):
        response = helpers.retrieve_patient(retrieve[5]["patient"], parameterized_headers)
        helpers.check_retrieve_response_body(response, retrieve[5]["response"])
        helpers.check_response_status_code(response, 400)


@pytest.mark.search_scenarios_success
class TestPDSSandboxSearchSuiteSuccess:
    """Sandbox PDS Search Scenarios. Checks performed: canned Response_Bodies, Status_Codes and Headers"""

    def test_sandbox_simple_search(self, additional_headers):
        scenario = "Simple Search"
        response = helpers.search_patient(search[scenario]["query_params"], additional_headers)
        helpers.check_search_response_body(response, search[scenario]["response"])
        helpers.check_response_status_code(response, 200)
        helpers.check_response_headers(response, additional_headers)

    def test_wildcard_search(self, additional_headers):
        scenario = "Wildcard Search"
        response = helpers.search_patient(search[scenario]["query_params"], additional_headers)
        helpers.check_search_response_body(response, search[scenario]["response"])
        helpers.check_response_status_code(response, 200)
        helpers.check_response_headers(response, additional_headers)

    def test_limited_results_search(self, additional_headers):
        scenario = "Limited Results Search"
        response = helpers.search_patient(search[scenario]["query_params"], additional_headers)
        helpers.check_search_response_body(response, search[scenario]["response"])
        helpers.check_response_status_code(response, 200)
        helpers.check_response_headers(response, additional_headers)

    def test_sandbox_date_range_search(self, additional_headers):
        scenario = "Date Range Search"
        response = helpers.search_patient(search[scenario]["query_params"], additional_headers)
        helpers.check_search_response_body(response, search[scenario]["response"])
        helpers.check_response_status_code(response, 200)
        helpers.check_response_headers(response, additional_headers)

    def test_fuzzy_search(self, additional_headers):
        scenario = "Fuzzy Search"
        response = helpers.search_patient(search[scenario]["query_params"], additional_headers)
        helpers.check_search_response_body(response, search[scenario]["response"])
        helpers.check_response_status_code(response, 200)
        helpers.check_response_headers(response, additional_headers)

    def test_restricted_patient_search(self, additional_headers):
        scenario = "Restricted Patient Search"
        response = helpers.search_patient(search[scenario]["query_params"], additional_headers)
        helpers.check_search_response_body(response, search[scenario]["response"])
        helpers.check_response_status_code(response, 200)
        helpers.check_response_headers(response, additional_headers)

    def test_unsuccessful_search_returns_empty_bundle(self, additional_headers):
        scenario = "Unsuccessful Search"
        response = helpers.search_patient(search[scenario]["query_params"], additional_headers)
        helpers.check_search_response_body(response, search[scenario]["response"])
        helpers.check_response_status_code(response, 200)
        helpers.check_response_headers(response, additional_headers)

    def test_default_parameters_search(self, additional_headers):
        scenario = "Default Parameters Search"
        response = helpers.search_patient(search[scenario]["query_params"], additional_headers)
        helpers.check_search_response_body(response, search[scenario]["response"])
        helpers.check_response_status_code(response, 200)
        helpers.check_response_headers(response, additional_headers)

    def test_sandbox_compound_given_name_search(self, additional_headers):
        scenario = "Compound Given Name Search"
        response = helpers.search_patient(search[scenario]["query_params"], additional_headers)
        helpers.check_search_response_body(response, search[scenario]["response"])
        helpers.check_response_status_code(response, 200)
        helpers.check_response_headers(response, additional_headers)

    def test_sandbox_multi_phone_search_returns_hit(self, additional_headers):
        scenario = "Default Parameters Search with Phone"
        response = helpers.search_patient(search[scenario]["query_params"], additional_headers)
        helpers.check_search_response_body(response, search[scenario]["response"])
        helpers.check_response_status_code(response, 200)
        helpers.check_response_headers(response, additional_headers)

    def test_sandbox_multi_phone_search_returns_empty_bundle(self, additional_headers):
        scenario = "Unsuccessful Search including Phone"
        response = helpers.search_patient(search[scenario]["query_params"], additional_headers)
        helpers.check_search_response_body(response, search[scenario]["response"])
        helpers.check_response_status_code(response, 200)
        helpers.check_response_headers(response, additional_headers)

    def test_sandbox_multi_email_search_returns_hit(self, additional_headers):
        scenario = "Default Parameters Search with Email"
        response = helpers.search_patient(search[scenario]["query_params"], additional_headers)
        helpers.check_search_response_body(response, search[scenario]["response"])
        helpers.check_response_status_code(response, 200)
        helpers.check_response_headers(response, additional_headers)

    def test_sandbox_multi_email_search_returns_empty_bundle(self, additional_headers):
        scenario = "Unsuccessful Search including Email"
        response = helpers.search_patient(search[scenario]["query_params"], additional_headers)
        helpers.check_search_response_body(response, search[scenario]["response"])
        helpers.check_response_status_code(response, 200)
        helpers.check_response_headers(response, additional_headers)

    def test_wildcard_search_with_phone(self, additional_headers):
        scenario = "Wildcard Search with Phone"
        response = helpers.search_patient(search[scenario]["query_params"], additional_headers)
        helpers.check_search_response_body(response, search[scenario]["response"])
        helpers.check_response_status_code(response, 200)
        helpers.check_response_headers(response, additional_headers)

    def test_wildcard_search_with_email(self, additional_headers):
        scenario = "Wildcard Search with Email"
        response = helpers.search_patient(search[scenario]["query_params"], additional_headers)
        helpers.check_search_response_body(response, search[scenario]["response"])
        helpers.check_response_status_code(response, 200)
        helpers.check_response_headers(response, additional_headers)

    def test_fuzzy_search_with_email(self, additional_headers):
        scenario = "Fuzzy Search with Email"
        response = helpers.search_patient(search[scenario]["query_params"], additional_headers)
        helpers.check_search_response_body(response, search[scenario]["response"])
        helpers.check_response_status_code(response, 200)
        helpers.check_response_headers(response, additional_headers)

    def test_fuzzy_search_with_phone(self, additional_headers):
        scenario = "Fuzzy Search with Phone"
        response = helpers.search_patient(search[scenario]["query_params"], additional_headers)
        helpers.check_search_response_body(response, search[scenario]["response"])
        helpers.check_response_status_code(response, 200)
        helpers.check_response_headers(response, additional_headers)

    def test_fuzzy_search_with_phone_email(self, additional_headers):
        scenario = "Fuzzy Search with Phone and Email"
        response = helpers.search_patient(search[scenario]["query_params"], additional_headers)
        helpers.check_search_response_body(response, search[scenario]["response"])
        helpers.check_response_status_code(response, 200)
        helpers.check_response_headers(response, additional_headers)

    def test_sandbox_simple_search_including_phone(self, additional_headers):
        scenario = "Simple Search including Phone"
        response = helpers.search_patient(search[scenario]["query_params"], additional_headers)
        helpers.check_search_response_body(response, search[scenario]["response"])
        helpers.check_response_status_code(response, 200)
        helpers.check_response_headers(response, additional_headers)

    def test_sandbox_simple_search_including_email(self, additional_headers):
        scenario = "Simple Search including Email"
        response = helpers.search_patient(search[scenario]["query_params"], additional_headers)
        helpers.check_search_response_body(response, search[scenario]["response"])
        helpers.check_response_status_code(response, 200)
        helpers.check_response_headers(response, additional_headers)

    def test_sandbox_simple_search_including_phone_and_email(self, additional_headers):
        scenario = "Simple Search including Phone and Email"
        response = helpers.search_patient(search[scenario]["query_params"], additional_headers)
        helpers.check_search_response_body(response, search[scenario]["response"])
        helpers.check_response_status_code(response, 200)
        helpers.check_response_headers(response, additional_headers)

    def test_sandbox_date_range_search_inc_phone(self, additional_headers):
        scenario = "Date Range Search including Phone"
        response = helpers.search_patient(search[scenario]["query_params"], additional_headers)
        helpers.check_search_response_body(response, search[scenario]["response"])
        helpers.check_response_status_code(response, 200)
        helpers.check_response_headers(response, additional_headers)

    def test_sandbox_date_range_search_inc_email(self, additional_headers):
        scenario = "Date Range Search including Email"
        response = helpers.search_patient(search[scenario]["query_params"], additional_headers)
        helpers.check_search_response_body(response, search[scenario]["response"])
        helpers.check_response_status_code(response, 200)
        helpers.check_response_headers(response, additional_headers)

    def test_sandbox_simple_search_including_phone_and_email_non_match(self, additional_headers):
        scenario = "Simple Search including Phone and Email Non-Match"
        response = helpers.search_patient(search[scenario]["query_params"], additional_headers)
        helpers.check_search_response_body(response, search[scenario]["response"])
        helpers.check_response_status_code(response, 200)
        helpers.check_response_headers(response, additional_headers)

    def test_restricted_patient_search_inc_phone_and_email(self, additional_headers):
        scenario = "Restricted Patient Search including Phone and Email"
        response = helpers.search_patient(search[scenario]["query_params"], additional_headers)
        helpers.check_search_response_body(response, search[scenario]["response"])
        helpers.check_response_status_code(response, 200)
        helpers.check_response_headers(response, additional_headers)

    def test_sandbox_multi_given_name_search_inc_phone_and_email(self, additional_headers):
        scenario = "Multi Given Name Search including Phone and Email"
        response = helpers.search_patient(search[scenario]["query_params"], additional_headers)
        helpers.check_search_response_body(response, search[scenario]["response"])
        helpers.check_response_status_code(response, 200)
        helpers.check_response_headers(response, additional_headers)


@pytest.mark.search_scenarios_error
class TestPDSSandboxSearchSuiteError:
    @pytest.mark.parametrize("parameterized_headers", [
        {},
        {"Prefer": "response-async"}
    ])
    def test_search_missing_x_request_id(self, parameterized_headers):
        scenario = "Missing X-Request-ID"
        response = helpers.search_patient(search[scenario]["query_params"], parameterized_headers)
        helpers.check_search_response_body(response, search[scenario]["response"])
        helpers.check_response_status_code(response, 400)

    def test_unsupported_operation_with_completely_invalid_params(self, additional_headers):
        scenario = "Unsupported Operation with Completely Invalid Params"
        response = helpers.search_patient(search[scenario]["query_params"], additional_headers)
        helpers.check_search_response_body(response, search[scenario]["response"])
        helpers.check_response_status_code(response, 400)
        helpers.check_response_headers(response, additional_headers)

    def test_unsupported_operation_with_invalid_param_and_family_birthdate(self, additional_headers):
        scenario = "Unsupported Operation with Invalid Param and Family Birthdate"
        response = helpers.search_patient(search[scenario]["query_params"], additional_headers)
        helpers.check_search_response_body(response, search[scenario]["response"])
        helpers.check_response_status_code(response, 400)
        helpers.check_response_headers(response, additional_headers)

    def test_invalid_date_format_search(self, additional_headers):
        scenario = "Invalid Date Format Search"
        response = helpers.search_patient(search[scenario]["query_params"], additional_headers)
        helpers.check_search_response_body(response, search[scenario]["response"])
        helpers.check_response_status_code(response, 400)
        helpers.check_response_headers(response, additional_headers)

    def test_too_few_parameters_search(self, additional_headers):
        scenario = "Too Few Parameters Search"
        response = helpers.search_patient(search[scenario]["query_params"], additional_headers)
        helpers.check_search_response_body(response, search[scenario]["response"])
        helpers.check_response_status_code(response, 400)
        helpers.check_response_headers(response, additional_headers)



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

        # helpers.check_response_headers(update_response, additional_headers)
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
