Feature: Unattended Access
  Authentication using the signed JWT method.

  Background:
    Given I determine whether an asid is required

  Scenario: PDS FHIR API accepts request with valid access token
    Given I am authenticating using unattended access
    And I have a valid access token
    And I have a request context

    When I GET a patient

    Then I get a 200 HTTP response
    And I get a Bundle resource in the response

  Scenario: PDS FHIR API rejects request with invalid access token
    Given I am authenticating using unattended access
    And I have an invalid access token
    And I have a request context

    When I GET a patient

    Then I get a 401 HTTP response
    And I get an error response
    And I get a diagnosis of Invalid Access Token

  Scenario: PDS FHIR API rejects request with missing access token
    Given I am authenticating using unattended access
    And I have no access token
    And I have a request context

    When I GET a patient

    Then I get a 401 HTTP response
    And I get an error response
    And I get a diagnosis of Invalid access token

  Scenario: PDS FHIR API rejects request with expired access token
    Given I am authenticating using unattended access
    And I have an expired access token
    And I have a request context

    When I GET a patient

    Then I get a 401 HTTP response
    And I get an error response
    And I get a diagnosis of expired access token

  Scenario: PDS FHIR API accepts request without user role ID
    Given I am authenticating using unattended access
    And I have a valid access token
    And I have a request context

    When I GET a patient without a user role ID

    Then I get a 200 HTTP response
    And I get a Bundle resource in the response

  Scenario: PDS FHIR API rejects request for more than one result
    Given I am authenticating using unattended access
    And I have a valid access token
    And I have a request context

    When I GET a patient asking for two results

    Then I get a 403 HTTP response
    And I get an error response
    And I get a diagnosis of insufficient permissions

  Scenario: PDS FHIR API accepts request for one result
    Given I am authenticating using unattended access
    And I have a valid access token
    And I have a request context

    When I GET a patient asking for one result

    Then I get a 200 HTTP response
    And I get a Bundle resource in the response

  Scenario: PDS FHIR API rejects synchronous PATCH requests
    Given I am authenticating using unattended access
    And I have a valid access token
    And I have a request context

    When I PATCH a patient and ommit the prefer header

    Then I get a 403 HTTP response
    And I get an error response
    And I get a diagnosis of insufficient permissions to use this method

  Scenario: App with pds-app-restricted-update attribute set to TRUE accepts PATCH requests
    Given I am authenticating using unattended access
    And I have a request context
    And I create a new app
    And I add the attribute pds-app-restricted-update to my app with the value TRUE
    And I add the scope urn:nhsd:apim:app:level3:personal-demographics-service
    And I have a valid access token using my app

    When I PATCH a patient
    Then I get a 200 HTTP response

  Scenario: App with pds-app-restricted-update attribute set to FALSE does not accept PATCH requests
    Given I am authenticating using unattended access
    And I have a request context
    And I create a new app
    And I add the attribute pds-app-restricted-update to my app with the value FALSE
    And I add the scope urn:nhsd:apim:app:level3:personal-demographics-service
    And I have a valid access token using my app

    When I PATCH a patient
    Then I get a 403 HTTP response

  Scenario: App with pds-app-restricted-update attribute set to TRUE and no scopes does not accept PATCH requests
    Given I am authenticating using unattended access
    And I have a request context
    And I create a new app
    And I add the attribute pds-app-restricted-update to my app with the value TRUE
    And I add the scope ""
    And I have a valid access token using my app

    When I PATCH a patient
    Then I get a 403 HTTP response
