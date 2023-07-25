# Changelog
## 2023-07-25
* Updated the Makefile to use the latest version of the hapifhir validator

## 2023-06-26
* Documentation: Added address-postalcode as a search parameter in personal-demographics.yaml

## 2023-06-09
* Updated various patient.json files to include email and phone telecom snippets via script updates
* Updated format_examples.py to add additional telecom email snippet to patient 9000000009 (not possible to do multiple examples in OAS 2.0 in yaml file)
* Updated duplicate_examples.sh to amend patient email addresses using sed for purposes of test data.
* Adding relevant additional scenarios and tests in scenarios.py and test_sandbox.py to support phone and email search parameters, including simple search with telecom, multiparam search with telecom, fuzzy search with telecom, date range search with telecom and wildcard search with telecom. Also included are searches using telecoms that yield no results and invalid param searches that yield 400 results.
* Updated/refactored patient-searcher.js. Added data to support new test cases/scenarios. Refactored to enable easier reading and less code re-use.

## 2023-06-14
* Documentation: added details regarding the newly supported address key type - UPRN
* Updated the sandbox mocks and test scenarios to include the UPRN changes

## 2023-06-06
* Added setup instructions to readme.md that better describe how to get the project running
* Update to document new email and phone filter functionality

## 2023-05-22
* Changed description of period object to make the data item referenced more generic.
* Changed description of behaviour for historic flag.
* Changed description of 'related people do not exist'.

## 2023-05-18
* Updated response patient-searcher.js to return defined response to search params that return no results in test sandbox so more
informative. Adjusted test scenario and test in test_sandbox.py to reflect this.
* PatientCompoundName.json added as was missing and update_examples.sh script was failing so is now generated in the duplicate_examples.sh script so that localhost can be started using command 'make sandbox' for local dev. Also, other sandbox mocks (Patient.json, Patient-Jayne-Smyth.json) were adjusted slightly when the update_examples.sh script was run with 'make  sandbox' command.

## 2023-04-14
* Updated the managing organization description to reflect the logic added in SPINEDEM-685

## 2023-04-14
* Documentation: Changed image in digital onboarding emphasis box

## 2023-03-09
* Documentation: Added emphasis box in digital onboarding section

## 2023-03-09
* Updated poerty.lock

## 2023-01-25
* Updated documentation and manifest for patient-access mode move to beta

## 2023-01-24
* Removed "metadata: read" in pr-lint.yaml, added "id-token: write"

## 2023-01-24
* Made permissions explicit for dependabot in pr-lint.yaml

## 2023-01-06
* Added new address tests, test_patient_with_no_address and test_patient_with_no_address_request_without_addres_id

## 2022-12-15
* Added tests for addresses
* Added verifyAddressIdNotPresentWhenRequired in requests-validator.js

## 2022-12-20
* Documentation: Changed wording on addresses

## 2022-12-15
* Updated schema to include new PDS-RemovalReasonExitCode
* Updated scearios.py

## 2022-12-12
* Documentation: Added section on error codes

## 2022-12-09
* Documentation: Added section on existing API users

## 2022-12-07
* Added new scenarios for missing access token error message

## 2022-12-05
* Updated redirect-uri to no longer point to the herokuapp

## 2022-11-21
* Updated postman_collection.json to fix import fail error

## 2022-11-11
* Documentation: Changed text around smart cards

## 2022-11-08
* Documentation: Changed text around access modes

## 2022-11-08
* Fix patient_access tests

## 2022-10-19
* Updated CORS policies to allow nhsd-end-user-organisation-ods

## 2022-10-10
* Documentation: "NHSD-End-User-Organisation-ODS" added as a paramter to "/Patient", "/Patient/{id}", and "Patient{id}/RelatedPerson"

## 2022-10-06
* Documentation: personal-demographics.yaml changes to fix rendering issues, removing redundant self-closing <a> tags, and using properly formatted <br> tags

## 2022-09-02
* Documentation: Updated the Onboarding section to point to the new Onboarding support information page.

## 2022-08-11
* Documentation: Updated the security pattern benefits table.

## 2022-08-05
* Documentation: Removed reference to Gazetter service API

## 2022-08-05
* Documentation: Reworded guidence around address checking

## 2022-08-03
* Added SPINEDEM to pr-lint.yaml ticket names
* Documentation: Added guidence around address checking

## 2022-07-18
* Updated azure location of client_id and client_secret for the test app

## 2022-07-18
* Updated azure location of client_id and client_secret for the test app

## 2022-06-14
* Documentation: Updated contact us guidence, now pointing to digital onboarding process
* Minor change to pr-lint.yaml around ticket names

## 2022-06-14
* Documentation: Updated contact us guidence, now pointing to digital onboarding process
* Minor change to pr-lint.yaml around ticket names

## 2022-06-07
* Documentation: Tweaks to related APIs from PDS Notifications general update

## 2022-06-07
* Documentation: Added more details about use cases for PDS Notifications API to Overview

## 2022-06-04
* Documentation: Changed wording and URLs around conformance

## 2022-05-18
* Test for patient access with scope sensitivity

## 2022-05-17
* Documentation: Remove reference to needing a PDS access request - point to digital onboarding instead.

## 2022-05-10
* Documentation: Changed text explaining access modes

## 2022-05-05
* Documentation: Reverted previous changes

## 2022-05-05
* Documentation: Changed text explaining access modes

## 2022-05-04
* Documentation: Removed non-digital instructions now that DOS takes care of it all

## 2022-05-03
* Fixed pr-lint.yaml to include dos tickets

## 2022-05-03
* Changed version of FHIR validator in Makefile from latest to 5.6.42

## 2022-04-28
* Documentation: Add tech conformance links to two new pages for each access mode

## 2022-04-27
* Documentation: Typos and formatting fro acces mode tables

## 2022-04-26
* Documentation: Updated table that referred to access modes

## 2022-04-07
* Documentation: Added links in Overview to which APIs for the "cannot" use cases

## 2022-04-07
* Documentation: Fixed typo

## 2022-04-06
* Documentation: Added Contact us link to personal-demographics.yaml

## 2022-03-24
* Documentation: Added reference of technical conformance

## 2022-03-24
* Documentation: Added tag to fix broken page link

## 2022-03-14
* Documentation: Updated URL in personal-demographics.yaml

## 2022-02-09
* Updated the oauth endpoint for the INT tests

## 2022-02-07
* Updated tests to use the new identity service mock
* Added pytest-docker to dependencies

## 2022-01-20
* Documentation: Changed wording in personal-demographics.yaml

## 2022-01-19
* Renamed NHSD-Patient header to NHSD-NHSLogin-User

## 2022-01-14
* Added mock identity service proxy to products

## 2022-01-13
* Added scenario for an app without and ASID interacting with an asid-required API Proxy
* Increased a wait time in application_restricted.feature

## 2022-01-05
* Documentation: Changed patch to PATCH

## 2022-01-05
* Documentation: Reworded the description for the Retry-After header

## 2022-01-05
* Documentation: Added service level section

## 2022-01-04
* Made new makefile target to genereate short version spec

## 2021-12-24
* Fixed a typo

## 2021-12-21
* Fixed a typo

## 2021-12-21
* Added schema and test for scenario organization

## 2021-12-20
* Reverted change to issue.details.coding.code

## 2021-12-17
* Documentation: Minor rewording of personal-demographics.yaml

## 2021-12-15
* Changed issue.code and issue.details.coding.code values for AppRestricted patch attempt error message
* Added an automated test

## 2021-12-15
* Changed more inline components from personal-demographics.yaml to refs

## 2021-12-13
* Reinstate the Extended Attributes shared flow - had to take this functionality out to deploy master to production as the shared flow wasn't yet deployed

## 2021-12-13
* Increased the rate limit in production to 350TPS
* Disabled Per-App Quota and SpikeArrest policies

## 2021-12-13
* Documentation: Changed contact URL to email

## 2021-12-10
* Added waits to application_restricted scenarios

## 2021-12-10
* Tests for per app permissions

## 2021-12-03
* Documentation: Updated onboarding steps

## 2021-12-03
* Moved some schemas in personal-demographics.yaml to be referenced internally
* Updated mock data
* Added minimal_bundle to in formatting scripts

## 2021-11-22
* Documentation: changed wording around smart cards, updated URLs

## 2021-11-19
* Documentation: changed wording of advice returning patient address

## 2021-11-11
* Removed apiproxy/policies
* Refactored patient access tests

## 2021-11-08
* Removed ratelimit and quota attributes on an API Product as they are no longer required

## 2021-11-08
* Changed tests to only validate response body contains expected nhs number

## 2021-11-02
* Fixed flaky test

## 2021-10-27
* Updated system url to fix failing tests
* Updated python packages

## 2021-10-26
* Implemented strategic ratelimiting

## 2021-10-22
* Added fuzzy match and history search parameters to patient-searcher.js

## 2021-10-22
* Added test for patient access header
* Created apigee_api.py

## 2021-10-20
* Removed deprecated build pipeline parameters

## 2021-10-20
* Removed deprecated build pipeline parameters

## 2021-10-20
* Updated postman collection

## 2021-10-19
* Documentation: Updated personal-demographics.yaml

## 2021-10-18
* Fixed test for searches with spaces in names

## 2021-10-18
* Added test for searches with spaces in names
* Updated sandbox readme

## 2021-10-12
* Documentation: Changed wording for onboarding steps

## 2021-09-30
* Documentation: Updated URLs for health care worker access modes

## 2021-09-28
* Fixed sandbox test errors

## 2021-09-23
* Increased rate limit to 20TPS

## 2021-09-06
* Reverted rate limiting back to 525 TPS

## 2021-09-03
* Increased sleep time in conftest.py from 1.5 to 2.5 seconds to reduce timeout errors

## 2021-09-03
* Fixed environment vairable in pds-test.yml

## 2021-09-02
* Added shared flow Ratelimiting

## 2021-08-20
* Updating spec to correctly list birthdate examples in 'Try this API'
* Updating spec and sandbox server to set up patient response for default 'Try this API' parameters

## 2020-08-19
* Adding `X-Request-ID` and `X-Correlation-ID` handling in apigee proxy and target

## 2020-07-14
* Changed `Polling` endpoint to `_poll`

## 2020-06-18
* Added `_ping` endpoint to check health state of the proxy
* Added payload to `_ping`, returning information about the deployed version

## 2020-05-28
* Adding Polling endpoint.

## 2020-05-27
* Added a step in pipeline to deploy the specification automatically
* Added a step in the workflow to add a link to the interal portal to the specification

## 2020-05-12
* Adding update JSON Patch description.
* Deceased Date Time and Death Notification Status Update descriptions.

## 2020-05-07
* Added Contact Preferences extension to the Patient resource
* Removed GET Related Person by Object ID

## 2020-04-30
* Remove TODO description
* Fix fhir validator download

## 2020-04-27
* Add new regression and smoke test packs
* Add a test runner for newman tests, which can auth with identity-service
* Additional changes to support running tests in release pipeline

## 2020-04-23
* Add step in pipeline to replace invalid characters in the branch name

## 2020-04-09
* No longer need to include `NHSD-Identity-JWT` header in API Calls

## 2020-04-08
* Adding Related Person endpoint to the Specification.

## 2020-03-31
* Move over to using Azure Pipelines for builds and releases.
* Some refactoring.

## 2020-03-20
* Update server urls to '.api.service.nhs.uk' domains in the OAS. Now includes Integration and Production environments.

## 2020-03-27
* Added `security` object to patient `meta` object

## 2020-03-18
* Additional check that required header `NHS-Session-URID` is not blank/empty when present

## 2020-03-16
* Validate JWT signature

## 2020-03-11
* Add business effective period for general practice

## 2020-03-09
* Add business effective period for all pharmacy extensions
* Created `identity-v1` OAuth API Proxy
* Secured PDS API Proxy Endpoints by requiring OAuth and JWT Tokens

## 2020-03-02
* Add `NHSD-Session-URID` header to specification.
* Rename `from_asid` header to `NHSD-ASID`
* New PDS sandbox search scenarios
* Updating `Name` prefixes and suffixes to be an array of string, not string
* Add dispensing doctor and medical appliance supplier extensions

## 2020-02-26
* Add a config for dependabot so that security updates are automatically merged

## 2020-02-24
* Hugely improved linting of source code
* New testing setup & approach to support e2e tests
* Updated CI to run regression tests
* API Proxy: Add `from_asid` header when communicating with `ig3` target endpoint
* API Proxy (ops): Deployment scripts and instructions now support 'personal' developer proxies

## 2020-02-17
* Add Apigee API Proxy definition to repository
* Make command to deploy API Proxy and Sandbox server
* Continuous integration task to deploy API Proxy

## 2020-02-13
* Fix caching process, which was breaking on master
* Auto-link JIRA tickets in pull requests

## 2020-02-12
* Cache libraries during builds
* Tag and release successful master builds, and upload release assets

## 2020-02-11
* Moved the CI/CD pipeline from circleci to github actions
* Fixed a bug in CI pipeline that stopped version being correctly calculated

## 2020-02-10
* Updated API spec search documentation

## 2020-02-06
* Updated API spec overview documentation to clarify FHIR extensions and other bits and bobs based on user feedback

## 2020-02-03
* Updated API spec to make description formats consistent
* Updated API spec to clarify meanings of nominated pharmacies and registered GPs

## 2020-01-31
* Updated pull request template
* Updated CONTRIBUTING.md
* Added a make target to update examples
* Removed a documentation reference to ods-site-code
* Changed API base URL
* Added a better example for address lines
* Removed ods-site-code as a possible value for code system to identify a nominated pharmacy on Patient.
* Fix some mistakes in the README that referred to a nonexistent directory: `publish` -> `dist`

## 2020-01-30
* Added automatic version calculation
* `make publish` now adds version into output oas file
* Added automatic version tagging to CI pipeline
* Added changelog
