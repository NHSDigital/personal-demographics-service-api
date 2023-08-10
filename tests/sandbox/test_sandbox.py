import pytest
from aiohttp import ClientResponse
from .data.scenarios import relatedPerson, retrieve, search, update
from .utils import helpers
from api_test_utils import env
from api_test_utils.api_session_client import APISessionClient
from api_test_utils.api_test_session_config import APITestSessionConfig


@pytest.mark.deployment_scenarios
class TestPDSSandboxDeploymentSuite:
    """Sandbox PDS Deployment Scenarios. Checks performed: status_codes and version deployed"""

    @pytest.mark.asyncio
    async def test_wait_for_ping(self, api_client: APISessionClient, api_test_config: APITestSessionConfig):
        async def apigee_deployed(response: ClientResponse):
            if response.status != 200:
                return False
            body = await response.json(content_type=None)
            return body.get("commitId") == api_test_config.commit_id

        await helpers.poll_until_v2(
            make_request=lambda: api_client.get("_ping"), until=apigee_deployed, timeout=30
        )

    @pytest.mark.asyncio
    async def test_check_status_is_secured(self, api_client: APISessionClient):
        async with api_client.get("_status", allow_retries=True) as response:
            assert response.status == 401

    @pytest.mark.asyncio
    async def test_wait_for_status(self, api_client: APISessionClient, api_test_config: APITestSessionConfig):
        async def is_deployed(response: ClientResponse):
            if response.status != 200:
                return False
            body = await response.json()

            if body.get("commitId") != api_test_config.commit_id:
                return False

            backend = helpers.dict_path(body, path=["checks", "healthcheck", "outcome", "version"])
            if not backend:
                return True

            return backend.get("commitId") == api_test_config.commit_id

        await helpers.poll_until_v2(
            make_request=lambda: api_client.get(
                "_status", headers={"apikey": env.status_endpoint_api_key()}
            ),
            until=is_deployed,
            timeout=120,
        )


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


@pytest.mark.search_scenarios
class TestPDSSandboxSearchSuite:
    """Sandbox PDS Search Scenarios. Checks performed: canned Response_Bodies, Status_Codes and Headers"""

    def test_sandbox_simple_search(self, additional_headers):
        response = helpers.search_patient(search[0]["query_params"], additional_headers)
        helpers.check_search_response_body(response, search[0]["response"])
        helpers.check_response_status_code(response, 200)
        helpers.check_response_headers(response, additional_headers)

    def test_sandbox_simple_search_including_phone(self, additional_headers):
        response = helpers.search_patient(search[22]["query_params"], additional_headers)
        helpers.check_search_response_body(response, search[22]["response"])
        helpers.check_response_status_code(response, 200)
        helpers.check_response_headers(response, additional_headers)

    def test_sandbox_simple_search_including_email(self, additional_headers):
        response = helpers.search_patient(search[23]["query_params"], additional_headers)
        helpers.check_search_response_body(response, search[23]["response"])
        helpers.check_response_status_code(response, 200)
        helpers.check_response_headers(response, additional_headers)

    def test_sandbox_simple_search_including_phone_and_email(self, additional_headers):
        response = helpers.search_patient(search[24]["query_params"], additional_headers)
        helpers.check_search_response_body(response, search[24]["response"])
        helpers.check_response_status_code(response, 200)
        helpers.check_response_headers(response, additional_headers)

    def test_sandbox_simple_search_including_phone_and_email_non_match(self, additional_headers):
        response = helpers.search_patient(search[27]["query_params"], additional_headers)
        helpers.check_search_response_body(response, search[27]["response"])
        helpers.check_response_status_code(response, 200)
        helpers.check_response_headers(response, additional_headers)

    def test_wildcard_search(self, additional_headers):
        response = helpers.search_patient(search[1]["query_params"], additional_headers)
        helpers.check_search_response_body(response, search[1]["response"])
        helpers.check_response_status_code(response, 200)
        helpers.check_response_headers(response, additional_headers)

    def test_limited_results_search(self, additional_headers):
        response = helpers.search_patient(search[2]["query_params"], additional_headers)
        helpers.check_search_response_body(response, search[2]["response"])
        helpers.check_response_status_code(response, 200)
        helpers.check_response_headers(response, additional_headers)

    def test_sandbox_date_range_search(self, additional_headers):
        response = helpers.search_patient(
            "family=Smith&gender=female&birthdate=ge2010-10-21&birthdate=le2010-10-23",
            additional_headers,
        )
        helpers.check_search_response_body(response, search[3]["response"])
        helpers.check_response_status_code(response, 200)
        helpers.check_response_headers(response, additional_headers)

    def test_sandbox_date_range_search_inc_phone(self, additional_headers):
        response = helpers.search_patient(
            "family=Smith&gender=female&birthdate=ge2010-10-21&birthdate=le2010-10-23&phone=01632960587",
            additional_headers,
        )
        helpers.check_search_response_body(response, search[25]["response"])
        helpers.check_response_status_code(response, 200)
        helpers.check_response_headers(response, additional_headers)

    def test_sandbox_date_range_search_inc_email(self, additional_headers):
        response = helpers.search_patient(
            "family=Smith&gender=female&birthdate=ge2010-10-21&birthdate=le2010-10-23&email=jane.smith@example.com",
            additional_headers,
        )
        helpers.check_search_response_body(response, search[26]["response"])
        helpers.check_response_status_code(response, 200)
        helpers.check_response_headers(response, additional_headers)

    def test_fuzzy_search(self, additional_headers):
        response = helpers.search_patient(search[4]["query_params"], additional_headers)
        helpers.check_search_response_body(response, search[4]["response"])
        helpers.check_response_status_code(response, 200)
        helpers.check_response_headers(response, additional_headers)

    def test_fuzzy_search_with_email(self, additional_headers):
        response = helpers.search_patient(search[18]["query_params"], additional_headers)
        helpers.check_search_response_body(response, search[18]["response"])
        helpers.check_response_status_code(response, 200)
        helpers.check_response_headers(response, additional_headers)

    def test_fuzzy_search_with_phone(self, additional_headers):
        response = helpers.search_patient(search[19]["query_params"], additional_headers)
        helpers.check_search_response_body(response, search[19]["response"])
        helpers.check_response_status_code(response, 200)
        helpers.check_response_headers(response, additional_headers)

    def test_fuzzy_search_with_phone_email(self, additional_headers):
        response = helpers.search_patient(search[20]["query_params"], additional_headers)
        helpers.check_search_response_body(response, search[20]["response"])
        helpers.check_response_status_code(response, 200)
        helpers.check_response_headers(response, additional_headers)

    def test_restricted_patient_search(self, additional_headers):
        response = helpers.search_patient(search[5]["query_params"], additional_headers)
        helpers.check_search_response_body(response, search[5]["response"])
        helpers.check_response_status_code(response, 200)
        helpers.check_response_headers(response, additional_headers)

    def test_restricted_patient_search_inc_phone_and_email(self, additional_headers):
        response = helpers.search_patient(search[28]["query_params"], additional_headers)
        helpers.check_search_response_body(response, search[28]["response"])
        helpers.check_response_status_code(response, 200)
        helpers.check_response_headers(response, additional_headers)

    def test_unsuccessful_search_returns_empty_bundle(self, additional_headers):
        response = helpers.search_patient(search[6]["query_params"], additional_headers)
        helpers.check_search_response_body(response, search[6]["response"])
        helpers.check_response_status_code(response, 200)
        helpers.check_response_headers(response, additional_headers)

    def test_invalid_date_format_search(self, additional_headers):
        response = helpers.search_patient(search[7]["query_params"], additional_headers)
        helpers.check_search_response_body(response, search[7]["response"])
        helpers.check_response_status_code(response, 400)
        helpers.check_response_headers(response, additional_headers)

    def test_too_few_parameters_search(self, additional_headers):
        response = helpers.search_patient("", additional_headers)
        helpers.check_search_response_body(response, search[8]["response"])
        helpers.check_response_status_code(response, 400)
        helpers.check_response_headers(response, additional_headers)

    def test_default_parameters_search(self, additional_headers):
        response = helpers.search_patient(search[9]["query_params"], additional_headers)
        helpers.check_search_response_body(response, search[9]["response"])
        helpers.check_response_status_code(response, 200)
        helpers.check_response_headers(response, additional_headers)

    def test_sandbox_multi_given_name_search(self, additional_headers):
        response = helpers.search_patient(search[10]["query_params"], additional_headers)
        helpers.check_search_response_body(response, search[10]["response"])
        helpers.check_response_status_code(response, 200)
        helpers.check_response_headers(response, additional_headers)

    def test_sandbox_multi_given_name_search_inc_phone_and_email(self, additional_headers):
        response = helpers.search_patient(search[29]["query_params"], additional_headers)
        helpers.check_search_response_body(response, search[29]["response"])
        helpers.check_response_status_code(response, 200)
        helpers.check_response_headers(response, additional_headers)

    def test_sandbox_multi_phone_search_returns_hit(self, additional_headers):
        response = helpers.search_patient(search[12]["query_params"], additional_headers)
        helpers.check_search_response_body(response, search[12]["response"])
        helpers.check_response_status_code(response, 200)
        helpers.check_response_headers(response, additional_headers)

    def test_sandbox_multi_email_search_returns_hit(self, additional_headers):
        response = helpers.search_patient(search[14]["query_params"], additional_headers)
        helpers.check_search_response_body(response, search[14]["response"])
        helpers.check_response_status_code(response, 200)
        helpers.check_response_headers(response, additional_headers)

    def test_sandbox_multi_phone_search_returns_empty_bundle(self, additional_headers):
        response = helpers.search_patient(search[13]["query_params"], additional_headers)
        helpers.check_search_response_body(response, search[13]["response"])
        helpers.check_response_status_code(response, 200)
        helpers.check_response_headers(response, additional_headers)

    def test_sandbox_multi_email_search_returns_empty_bundle(self, additional_headers):
        response = helpers.search_patient(search[15]["query_params"], additional_headers)
        helpers.check_search_response_body(response, search[15]["response"])
        helpers.check_response_status_code(response, 200)
        helpers.check_response_headers(response, additional_headers)

    def test_wildcard_search_with_phone(self, additional_headers):
        response = helpers.search_patient(search[16]["query_params"], additional_headers)
        helpers.check_search_response_body(response, search[16]["response"])
        helpers.check_response_status_code(response, 200)
        helpers.check_response_headers(response, additional_headers)

    def test_wildcard_search_with_email(self, additional_headers):
        response = helpers.search_patient(search[17]["query_params"], additional_headers)
        helpers.check_search_response_body(response, search[17]["response"])
        helpers.check_response_status_code(response, 200)
        helpers.check_response_headers(response, additional_headers)

    def test_unsupported_operation_with_invalid_param_and_family_birthdate(self, additional_headers):
        response = helpers.search_patient(search[11]["query_params"], additional_headers)
        helpers.check_search_response_body(response, search[11]["response"])
        helpers.check_response_status_code(response, 400)
        helpers.check_response_headers(response, additional_headers)

    def test_unsupported_operation_with_completely_invalid_params(self, additional_headers):
        response = helpers.search_patient(search[21]["query_params"], additional_headers)
        helpers.check_search_response_body(response, search[21]["response"])
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
        helpers.check_response_status_code(update_response, 412)

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
