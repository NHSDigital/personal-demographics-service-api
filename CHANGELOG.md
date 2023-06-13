# Changelog
## 2023-06-13
* Documentation: Added address-postalcode as a search parameter in personal-demographics.yaml

## 2023-05-18
* Updated response patient-searcher.js to return defined response to search params that return no results in test sandbox so more
informative. Adjusted test scenario and test in test_sandbox.py to reflect this.
* PatientCompoundName.json added as was missing and update_examples.sh script was failing so is now generated in the            duplicate_examples.sh script so that localhost can be started using command 'make sandbox' for local dev. Also, other sandbox mocks (Patient.json, Patient-Jayne-Smyth.json) were adjusted slightly when the update_examples.sh script was run with 'make  sandbox' command.

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
