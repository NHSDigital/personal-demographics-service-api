# Changelog

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
