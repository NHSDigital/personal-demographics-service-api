Feature: Unattended Access
  Authentication using the signed JWT method.

  Background:
    Given I determine whether an asid is required

  Scenario: PDS FHIR API accepts request with valid access token
    Given I am authenticating using unattended access
    And I have a request context
    And I have a valid access token

    When I GET a patient

    Then I get a 200 HTTP response
    And I get a Bundle resource in the response


  Scenario: PDS FHIR API rejects request with missing authorization header
    Given I am authenticating using unattended access
    And I have no Authorization header
    And I have a request context

    When I GET a patient

    Then I get a 401 HTTP response
    And I get an error response
    And the error issue.diagnostics value is Missing authorization header


  Scenario: PDS FHIR API rejects request with an empty authorization header
    Given I am authenticating using unattended access
    And I have an empty Authorization header
    And I have a request context

    When I GET a patient

    Then I get a 401 HTTP response
    And I get an error response
    And the error issue.diagnostics value is Empty authorization header

  Scenario: PDS FHIR API rejects request with invalid access token
    Given I am authenticating using unattended access
    And I have an invalid access token
    And I have a request context

    When I GET a patient

    Then I get a 401 HTTP response
    And I get an error response
    And the error issue.diagnostics value is Invalid Access Token


  Scenario: PDS FHIR API rejects request with missing access token
    Given I am authenticating using unattended access
    And I have no access token
    And I have a request context

    When I GET a patient

    Then I get a 401 HTTP response
    And I get an error response
    And the error issue.diagnostics value is Missing access token


  Scenario: PDS FHIR API rejects request with expired access token
    Given I am authenticating using unattended access
    And I have a request context
    And I have an expired access token

    When I GET a patient

    Then I get a 401 HTTP response
    And I get an error response
    And the error issue.diagnostics value is Access Token expired


  Scenario: PDS FHIR API accepts request without user role ID
    Given I am authenticating using unattended access
    And I have a request context
    And I have a valid access token

    When I GET a patient without a user role ID

    Then I get a 200 HTTP response
    And I get a Bundle resource in the response

  Scenario: PDS FHIR API rejects request for more than one result
    Given I am authenticating using unattended access
    And I have a request context
    And I have a valid access token

    When I GET a patient asking for two results

    Then I get a 403 HTTP response
    And I get an error response
    And the error issue.diagnostics value is Your app has insufficient permissions to perform this search. Please contact support.


  Scenario: PDS FHIR API accepts request for one result
    Given I am authenticating using unattended access
    And I have a request context
    And I have a valid access token

    When I GET a patient asking for one result

    Then I get a 200 HTTP response
    And I get a Bundle resource in the response

  Scenario: PDS FHIR API rejects synchronous PATCH requests
    Given I am authenticating using unattended access
    And I have a request context
    And I have a valid access token

    When I PATCH a patient and ommit the prefer header

    Then I get a 403 HTTP response
    And I get an error response
    And the error issue.diagnostics value is Your app has insufficient permissions to use this method. Please contact support.


  Scenario: App with pds-app-restricted-update attribute set to TRUE accepts PATCH requests
    Given I am authenticating using unattended access
    And I have a request context
    And I create a new app
    And I add the attribute with key of apim-app-flow-vars and a value of { "pds" : { "app-restricted": { "update": true } }}
    And I add the scope urn:nhsd:apim:app:level3:personal-demographics-service
    And I wait for 200 milliseconds
    And I have a valid access token

    When I PATCH a patient
    Then I get a 200 HTTP response

  Scenario: App with pds-app-restricted-update attribute set to FALSE does not accept PATCH requests
    Given I am authenticating using unattended access
    And I have a request context
    And I create a new app
    And I add the attribute with key of apim-app-flow-vars and a value of { "pds" : { "app-restricted": { "update": false } }}
    And I add the scope urn:nhsd:apim:app:level3:personal-demographics-service
    And I wait for 100 milliseconds
    And I have a valid access token

    When I PATCH a patient
    Then I get a 403 HTTP response

  Scenario: App with pds-app-restricted-update attribute set to TRUE and invalid app restricted scope does not allow a PATCH
    Given I am authenticating using unattended access
    And I have a request context
    And I create a new app
    And I add the attribute with key of apim-app-flow-vars and a value of { "pds" : { "app-restricted": { "update": true } }}
    And I add the scope urn:nhsd:apim:app:level3:reasonable-adjustment-flag
    And I wait for 200 milliseconds
    And I have a valid access token

    When I PATCH a patient
    Then I get a 403 HTTP response


  Scenario: PDS FHIR API rejects app restricted update
    Given I am authenticating using unattended access
    And I have a request context
    And I have a valid access token

    When I PATCH a patient

    Then I get a 403 HTTP response
    And I get an error response
    And the error issue.code value is forbidden
    And the error issue.details.coding.code value is INVALID_METHOD
    And the error issue.details.coding.display value is Cannot update resource with Application-Restricted access token
    And the error issue.diagnostics value is Your app has insufficient permissions to use this method. Please contact support.

  Scenario: App without an ASID fails in an asid-required API Proxy
    Given I am authenticating using unattended access
    And I have a request context
    And I create a new app
    And I wait for 100 milliseconds    

    When I GET a patient
    Then I get a 400 HTTP response
    And the error issue.diagnostics value is No ASID is associated with your app. Please contact support.

  Scenario: App WITH an ASID works in an asid-required API Proxy
    Given I am authenticating using unattended access
    And I have a request context
    And I create a new app
    And I add an asid attribute
    And I wait for 200 milliseconds

    When I GET a patient
    Then I get a 200 HTTP response

