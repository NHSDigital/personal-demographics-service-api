# Changelog

## 2020-02-11
* Moved the CI/CD pipeline from circleci to github actions

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
