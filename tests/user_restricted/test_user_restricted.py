import json
from .data.pds_scenarios import retrieve, search, update
from .utils import helpers
import pytest
from pytest_check import check


class TestUserRestrictedRetrievePatient:

    def test_retrieve_deprecated_url(self, headers_with_token):
        response = helpers.retrieve_patient_deprecated_url(
            retrieve[0]["patient"],
            self.headers
        )

        helpers.check_response_status_code(response, 404)

    @pytest.mark.smoke_test
    def test_retrieve_patient(self, headers_with_token):
        response = helpers.retrieve_patient(
            retrieve[0]["patient"],
            self.headers
        )
        helpers.check_response_headers(response, self.headers)
        helpers.check_response_status_code(response, 200)
        helpers.check_retrieve_response_body_shape(response)

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

    def test_user_role_sharedflow_retrieve_patient_with_missing_urid_header(self, headers_with_token):
        self.headers.pop("NHSD-Session-URID")
        response = helpers.retrieve_patient(
            retrieve[0]["patient"],
            self.headers
        )
        helpers.check_response_status_code(response, 200)
        helpers.check_retrieve_response_body_shape(response)
        helpers.check_response_headers(response, self.headers)

    def test_user_role_sharedflow_invalid_role(self, headers_with_token):
        self.headers["NHSD-Session-URID"] = "invalid"
        response = helpers.retrieve_patient(
            retrieve[8]["patient"],
            self.headers
        )
        helpers.check_retrieve_response_body(response, retrieve[8]["response"])
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

    @pytest.mark.smoke_test
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

    def test_search_patient_with_blank_auth_header_at(self, headers_with_token):
        self.headers['Authorization'] = ''
        response = helpers.search_patient(
            search[1]["query_params"],
            self.headers
        )
        helpers.check_search_response_body(response, search[1]["response"])
        helpers.check_response_status_code(response, 401)
        helpers.check_response_headers(response, self.headers)

    def test_search_patient_with_invalid_auth_header(self, headers):
        headers['authorization'] = 'Bearer abcdef123456789'
        response = helpers.search_patient(
            search[2]["query_params"],
            headers
        )
        helpers.check_search_response_body(response, search[2]["response"])
        helpers.check_response_status_code(response, 401)
        helpers.check_response_headers(response, headers)

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

    def test_search_patient_happy_path_sensitive(self, headers_with_token):
        response = helpers.search_patient(
            search[9]["query_params"],
            self.headers
        )
        helpers.check_search_response_body(response, search[9]["response"])
        helpers.check_response_status_code(response, 200)
        helpers.check_response_headers(response, self.headers)

    def test_search_patient_sensitive_info_not_returned(self, headers_with_token):
        response = helpers.search_patient(
            search[10]["query_params"],
            self.headers
        )
        helpers.check_search_response_body(response, search[10]["response"])
        helpers.check_response_status_code(response, 200)
        helpers.check_response_headers(response, self.headers)

    def test_search_patient_happy_path_genderfree(self, headers_with_token):
        response = helpers.search_patient(
            search[7]["query_params"],
            self.headers
        )
        helpers.check_search_response_body(response, search[0]["response"])
        helpers.check_response_status_code(response, 200)
        helpers.check_response_headers(response, self.headers)

    def test_search_advanced_alphanumeric_genderfree(self, headers_with_token):
        response = helpers.search_patient(
            search[8]["query_params"],
            self.headers
        )
        helpers.check_search_response_body(response, search[0]["response"])
        helpers.check_response_status_code(response, 200)
        helpers.check_response_headers(response, self.headers)

    def test_simple_trace_no_gender(self, headers_with_token):
        """See TestBase37101 Chain 7001"""
        print(self.headers)
        response = helpers.search_patient(
            {"family": "JAMESONGLE", "birthdate": "1982-03-14"},
            self.headers
        )
        response_body = response.json()

        assert response.status_code == 200
        assert response_body["resourceType"] == "Bundle"
        assert response_body["type"] == "searchset"
        assert response_body["total"] == 1
        assert response_body["entry"][0]["resource"]["id"] == "9912003071"

    def test_simple_trace_no_gender_no_result(self, headers_with_token):
        """See TestBase37101 Chain 7002"""
        print(self.headers)
        response = helpers.search_patient(
            {"family": "Clarke", "birthdate": "1975-01-01"},
            self.headers
        )
        response_body = response.json()

        assert response.status_code == 200
        assert response_body["resourceType"] == "Bundle"
        assert response_body["type"] == "searchset"
        assert response_body["total"] == 0

    def test_no_gender_postcode_format_doesnt_affect_score(self, headers_with_token):
        """See TestBase37101 Chain 7003"""
        response_1 = helpers.search_patient(
            {"family": "JAMESONGLE", "birthdate": "1982-03-14", "address-postcode": "LS27 8RR"},
            self.headers
        )
        response_1_body = response_1.json()

        response_2 = helpers.search_patient(
            {"family": "JAMESONGLE", "birthdate": "1982-03-14", "address-postcode": "ls278rr"},
            self.headers
        )
        response_2_body = response_2.json()

        assert response_1.status_code == 200
        assert response_2.status_code == response_1.status_code
        assert response_1_body["entry"][0]["resource"]["id"] == "9912003071"
        assert response_1_body["entry"][0]["resource"]["id"] == response_2_body["entry"][0]["resource"]["id"]
        assert response_1_body["entry"][0]["search"]["score"] == 1
        assert response_1_body["entry"][0]["search"]["score"] == response_2_body["entry"][0]["search"]["score"]

    def test_algorithmic_search_without_gender(self, headers_with_token):
        """See TestBase37102 Chain 7001"""
        response = helpers.search_patient(
            {"family": "STSimilar01", "birthdate": "1975-01-01"},
            self.headers
        )
        response_body = response.json()

        assert response.status_code == 200
        assert response_body["type"] == "searchset"
        assert response_body["resourceType"] == "Bundle"
        assert response_body["total"] == 3
        assert response_body["entry"][0]["search"]["score"] == 1
        assert response_body["entry"][0]["resource"]["id"] == "9990000050"
        assert response_body["entry"][0]["resource"]["gender"] == "male"
        assert response_body["entry"][0]["resource"]["birthDate"] == "1975-01-01"
        assert response_body["entry"][1]["search"]["score"] == 1
        assert response_body["entry"][1]["resource"]["id"] == "9990000069"
        assert response_body["entry"][1]["resource"]["gender"] == "male"
        assert response_body["entry"][1]["resource"]["birthDate"] == "1975-01-01"
        assert response_body["entry"][2]["search"]["score"] == 1
        assert response_body["entry"][2]["resource"]["id"] == "9990000077"
        assert response_body["entry"][2]["resource"]["gender"] == "male"
        assert response_body["entry"][2]["resource"]["birthDate"] == "1975-01-01"

    def test_algorithmic_fuzzy_match_unknown_gender(self, headers_with_token):
        """See TestBase37104 Chain 0001"""
        response = helpers.search_patient(
            {"family": "ATUnknow", "given": "Nisha", "birthdate": "1980-09-19", "_fuzzy-match": "true"},
            self.headers
        )
        response_body = response.json()

        assert response.status_code == 200
        assert response_body["type"] == "searchset"
        assert response_body["resourceType"] == "Bundle"
        assert response_body["entry"][0]["search"]["score"] == 0.9896
        assert response_body["entry"][0]["resource"]["id"] == "9990001502"

    def test_algorithmic_fuzzy_match_unicode(self, headers_with_token):
        """See TestBase37104 Chain 0007"""
        response = helpers.search_patient(
            {"family": "PÀTSÖN", "given": "PÀULINÉ", "birthdate": "1979-07-27", "_fuzzy-match": "true"},
            self.headers
        )
        response_body = response.json()

        assert response.status_code == 200
        assert response_body["type"] == "searchset"
        assert response_body["resourceType"] == "Bundle"
        assert response_body["entry"][0]["search"]["score"] == 0.9806
        assert response_body["entry"][0]["resource"]["id"] == "9930000011"
        assert response_body["entry"][0]["resource"]["gender"] == "female"
        assert response_body["entry"][0]["resource"]["birthDate"] == "1979-07-27"
        assert response_body["entry"][0]["resource"]["name"][0]["family"] == "PÀTTISÖN"
        assert response_body["entry"][0]["resource"]["name"][0]["given"][0] == "PÀULINÉ"
        assert response_body["entry"][1]["search"]["score"] == 0.8595
        assert response_body["entry"][1]["resource"]["id"] == "9930000054"
        assert response_body["entry"][1]["resource"]["gender"] == "female"
        assert response_body["entry"][1]["resource"]["birthDate"] == "1979-07-27"

    def test_algorithmic_fuzzy_match_regular_returns_unicode(self, headers_with_token):
        """See TestBase37104 Chain 0008"""
        response = helpers.search_patient(
            {"family": "PATSON", "given": "PAULINE", "birthdate": "1979-07-27", "_fuzzy-match": "true"},
            self.headers
        )
        response_body = response.json()

        assert response.status_code == 200
        assert response_body["type"] == "searchset"
        assert response_body["resourceType"] == "Bundle"
        assert response_body["entry"][0]["search"]["score"] == 0.9806
        assert response_body["entry"][0]["resource"]["id"] == "9930000054"
        assert response_body["entry"][0]["resource"]["gender"] == "female"
        assert response_body["entry"][0]["resource"]["birthDate"] == "1979-07-27"
        assert response_body["entry"][0]["resource"]["name"][0]["family"] == "PATTISON"
        assert response_body["entry"][0]["resource"]["name"][0]["given"][0] == "PAULINE"
        assert response_body["entry"][1]["search"]["score"] == 0.8595
        assert response_body["entry"][1]["resource"]["id"] == "9930000011"
        assert response_body["entry"][1]["resource"]["gender"] == "female"
        assert response_body["entry"][1]["resource"]["birthDate"] == "1979-07-27"

    def test_algorithmic_fuzzy_match_for_birthdate_range(self, headers_with_token):
        """See TestBase37104 Chain 0009"""
        response = helpers.search_patient(
            "family=ATUnknow&given=Nisha&birthdate=le1990-09-19&birthdate=ge1970-09-19&_fuzzy-match=true",
            self.headers
        )
        response_body = response.json()

        assert response.status_code == 200
        assert response_body["type"] == "searchset"
        assert response_body["resourceType"] == "Bundle"
        assert response_body["entry"][0]["search"]["score"] == 0.9896
        assert response_body["entry"][0]["resource"]["id"] == "9990001502"

    def test_algorithmic_exact_match_requested_but_not_found(self, headers_with_token):
        """See TestBase37105 Chain 0003"""
        response = helpers.search_patient(
            {
                "family": "PÀTSÖN", "given": "PÀULINÉ", "birthdate": "1979-07-27",
                "_fuzzy-match": "true", "_exact-match": "true"
            },
            self.headers
        )
        response_body = response.json()

        assert response.status_code == 200
        assert response_body["type"] == "searchset"
        assert response_body["resourceType"] == "Bundle"
        assert response_body["total"] == 0

    def test_algorithmic_requesting_50_results(self, headers_with_token):
        """See TestBase37107 Chain 0004"""
        response = helpers.search_patient(
            {
                "family": "PATSON", "given": "PAULINE", "birthdate": "1979-07-27",
                "_fuzzy-match": "true", "_max-results": "50"
            },
            self.headers
        )
        response_body = response.json()

        assert response.status_code == 200
        assert response_body["type"] == "searchset"
        assert response_body["resourceType"] == "Bundle"
        assert response_body["entry"][0]["search"]["score"] == 0.9806
        assert response_body["entry"][0]["resource"]["id"] == "9930000054"
        assert response_body["entry"][1]["search"]["score"] == 0.8595

    def test_algorithmic_requesting_1_result_too_many_matches(self, headers_with_token):
        """See TestBase37107 Chain 0008"""
        response = helpers.search_patient(
            {
                "family": "PATSON", "given": "PAULINE", "birthdate": "1979-07-27",
                "_fuzzy-match": "true", "_max-results": "1"
            },
            self.headers
        )
        response_body = response.json()

        assert response_body["resourceType"] == "OperationOutcome"
        assert response_body["issue"][0]["details"]["coding"][0]["code"] == "TOO_MANY_MATCHES"
        assert response_body["issue"][0]["details"]["coding"][0]["display"] == "Too Many Matches"

    def test_simple_search_family_name_still_required(self, headers_with_token):
        response = helpers.search_patient(
            {"given": "PAULINE", "birthdate": "1979-07-27"},
            self.headers
        )
        response_body = response.json()

        assert response.status_code == 400
        assert response_body["resourceType"] == "OperationOutcome"
        assert response_body["issue"][0]["details"]["coding"][0]["code"] == "INVALID_SEARCH_DATA"

    def test_simple_search_birthdate_still_required(self, headers_with_token):
        response = helpers.search_patient(
            {"family": "PATSON", "given": "PAULINE"},
            self.headers
        )
        response_body = response.json()

        assert response.status_code == 400
        assert response_body["resourceType"] == "OperationOutcome"
        assert response_body["issue"][0]["details"]["coding"][0]["code"] == "MISSING_VALUE"

    def test_search_for_similar_patient_different_genders(self, headers_with_token):
        """Performing a gender-free search where there exists four patients with the same
        name and date of birth, but differing gender values, should return multiple distinct results."""

        family = "Brown"
        given = "Ann"
        birth_date = "1981-01-01"

        genders = ['male', 'female', 'other', 'unknown']
        patient_ids = ['5900025055', '5900027759', '5900028976', '5900037347']

        # Do the individual items exist and can be retrieved with a gendered search?
        for i, gender in enumerate(genders):
            patient_id = patient_ids[i]
            response = helpers.search_patient(
                {"family": family, "given": given, "birthdate": birth_date, "gender": gender},
                self.headers
            )
            response_body = response.json()

            assert response.status_code == 200
            assert response_body["type"] == "searchset"
            assert response_body["resourceType"] == "Bundle"
            assert response_body["total"] == 1
            assert response_body["entry"][0]["resource"]["id"] == patient_id
            assert response_body["entry"][0]["resource"]["gender"] == gender
            assert response_body["entry"][0]["resource"]["name"][0]["family"] == family
            assert response_body["entry"][0]["resource"]["name"][0]["given"][0] == given

        # Then retrieve and check for all of them with a genderless search
        response_all = helpers.search_patient(
            {"family": family, "given": given, "birthdate": birth_date},
            self.headers
        )
        response_all_body = response_all.json()

        assert response_all.status_code == 200
        assert response_all_body["type"] == "searchset"
        assert response_all_body["resourceType"] == "Bundle"
        assert response_all_body["total"] == 4

        # Order of search results is not guaranteed.
        # We will enumerate each one and make sure
        # it is unique and expected (ie from our genders,
        # and patient_ids lists)
        checked_results_count = 0
        for result in response_all_body["entry"]:
            i = genders.index(result["resource"]["gender"])
            patient_id, gender = patient_ids.pop(i), genders.pop(i)

            assert result["resource"]["id"] == patient_id
            assert result["resource"]["gender"] == gender
            assert result["resource"]["name"][0]["family"] == family
            assert result["resource"]["name"][0]["given"][0] == given

            checked_results_count += 1
        assert checked_results_count == 4


class TestUserRestrictedPatientUpdateSyncWrap:
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
        self.headers["X-Sync-Wait"] = "29"

        # Prefer header deprecated check that it still returns 200 response
        self.headers["Prefer"] = "respond-async"

        update_response = helpers.update_patient(
            update[0]["patient"],
            patient_record,
            update[0]["patch"],
            self.headers
        )
        with check:
            assert (json.loads(update_response.text))["birthDate"] == self.new_date
        with check:
            assert int((json.loads(update_response.text))["meta"]["versionId"]) == int(versionId) + 1
        helpers.check_response_status_code(update_response, 200)

    def test_update_patient_dob_with_invalid_x_sync_wait_header(self, headers_with_token, create_random_date):
        #  send retrieve patient request to retrieve the patient record (Etag Header) & versionId
        def retrieve_patient():
            response = helpers.retrieve_patient(
                update[0]["patient"],
                self.headers
            )
            return response

        response = retrieve_patient()

        patient_record = response.headers["Etag"]
        versionId = (json.loads(response.text))["meta"]["versionId"]
        # add the new dob to the patch, send the update and check the response
        update[0]["patch"]["patches"][0]["value"] = self.new_date

        self.headers["X-Sync-Wait"] = "invalid"

        update_response = helpers.update_patient(
            update[0]["patient"],
            patient_record,
            update[0]["patch"],
            self.headers
        )

        def assert_update_response(update_response):
            with check:
                assert (json.loads(update_response.text))["birthDate"] == self.new_date
            with check:
                assert int((json.loads(update_response.text))["meta"]["versionId"]) == int(versionId) + 1
            helpers.check_response_status_code(update_response, 200)

        if update_response.status_code == 503 and json.loads(
                update_response.text, strict=False)["issue"][0]["code"] == "timeout":
            """
                Temp fix due to slow VEIT07 env causing update to exceed default X-Sync-Wait timeout of 10s.
                If the update times out retrieve the patient instead and check if the record has been updated.
            """
            retrieve_response = retrieve_patient()
            assert_update_response(retrieve_response)
        else:
            assert_update_response(update_response)

    def test_update_patient_dob_with_low_sync_wait_timeout(self, headers_with_token, create_random_date):
        #  send retrieve patient request to retrieve the patient record (Etag Header) & versionId
        response = helpers.retrieve_patient(
            update[0]["patient"],
            self.headers
        )
        patient_record = response.headers["Etag"]

        # add the new dob to the patch, send the update and check the response
        update[0]["patch"]["patches"][0]["value"] = self.new_date

        self.headers["X-Sync-Wait"] = "0.25"
        update_response = helpers.update_patient(
            update[0]["patient"],
            patient_record,
            update[0]["patch"],
            self.headers
        )

        helpers.check_response_status_code(update_response, 503)

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


class TestUserRestrictedRetrieveRelatedPerson:

    @pytest.mark.smoke_test
    def test_retrieve_related_person(self, headers_with_token):
        response = helpers.retrieve_patient_related_person(
            retrieve[7]["patient"],
            self.headers
        )
        helpers.check_retrieve_related_person_response_body(response, retrieve[7]["response"])
        helpers.check_response_status_code(response, 200)
        helpers.check_response_headers(response, self.headers)


@pytest.mark.smoke_test
class TestStatusEndpoints:

    def test_ping_endpoint(self):
        response = helpers.ping_request()
        helpers.check_response_status_code(response, 200)

    def test_health_check_endpoint(self, headers_with_token):
        response = helpers.check_health_check_endpoint(self.headers)
        helpers.check_response_status_code(response, 200)
