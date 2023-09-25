Feature: Healthcare Worker Access
    Access by a healthcare worker

    Scenario: Healthcare worker using deprecated url
        Given I am a healthcare worker
        And I am using the deprecated url

        When I retrieve a patient

        Then I get a 404 HTTP response
    
    Scenario: Healthcare worker can retrieve patient
        Given I am a healthcare worker

        When I retrieve a patient

        Then I get a 200 HTTP response
        And the X-Request-ID response header matches the request
        And the X-Correlation-ID response header matches the request
        And the response body contains the patient id
        And the response body is the correct shape

    Scenario: Attempt to retrieve a patient with missing authorization header
        Given I am a healthcare worker
        And I don't have an Authorization header

        When I retrieve a patient

        Then I get a 401 HTTP response
        And the X-Request-ID response header matches the request
        And the X-Correlation-ID response header matches the request
        And the response body does not contain id
        And the response body is the Missing Authorization header reponse

    Scenario: Attempt to retrieve a patient with an empty authorization header
        Given I am a healthcare worker
        And I have an empty Authorization header

        When I retrieve a patient

        Then I get a 401 HTTP response
        And the X-Request-ID response header matches the request
        And the X-Correlation-ID response header matches the request
        And the response body does not contain id
        And the response body is the Empty Authorization header reponse

    Scenario: Attempt to retrieve a patient with an invalid authorization header
        Given I am a healthcare worker
        And I have an invalid Authorization header

        When I retrieve a patient

        Then I get a 401 HTTP response
        And the X-Request-ID response header matches the request
        And the X-Correlation-ID response header matches the request
        And the response body does not contain id
        And the response body is the Invalid Access Token reponse

    Scenario: Attempt to retrieve a patient without stating a role
        Given I am a healthcare worker
        And I don't have a NHSD-Session-URID header

        When I retrieve a patient

        Then I get a 400 HTTP response
        And the X-Request-ID response header matches the request
        And the X-Correlation-ID response header matches the request
        And the response body does not contain id
        And the response body is the Missing URID header reponse

    Scenario: Attempt to retrieve a patient with an invalid role
        Given I am a healthcare worker
        And I have an invalid NHSD-Session-URID header

        When I retrieve a patient

        Then I get a 400 HTTP response
        And the X-Request-ID response header matches the request
        And the X-Correlation-ID response header matches the request
        And the response body does not contain id
        And the response body is the Invalid URID header reponse

    Scenario: Attempt to retrieve a patient without Request ID header
        Given I am a healthcare worker
        And I have an empty X-Request-ID header

        When I retrieve a patient

        Then I get a 400 HTTP response
        And the X-Correlation-ID response header matches the request
        And the response header does not contain X-Request-ID
        And the response body does not contain id
        And the response body is the Empty X-Request ID reponse