Feature: Healthcare Worker Access (Retrieve)
    Retrieve a PDS record as a healthcare worker

    Scenario: Healthcare worker using deprecated url
        Given I am a healthcare worker user
        And I am using the deprecated url

        When I retrieve a patient

        Then I get a 404 HTTP response code
    
    Scenario: Healthcare worker can retrieve patient
        Given I am a healthcare worker user

        When I retrieve a patient

        Then I get a 200 HTTP response code
        And the X-Request-ID response header matches the request
        And the X-Correlation-ID response header matches the request
        And the response body contains the patient's NHS number
        And the response body is the correct shape

    Scenario: Attempt to retrieve a patient with missing authorization header
        Given I am a healthcare worker user
        And I don't have an Authorization header

        When I retrieve a patient

        Then I get a 401 HTTP response code
        And the X-Request-ID response header matches the request
        And the X-Correlation-ID response header matches the request
        And the response body does not contain id
        And the response body is the Missing Authorization header response

    Scenario: Attempt to retrieve a patient with an empty authorization header
        Given I am a healthcare worker user
        And I have an empty Authorization header

        When I retrieve a patient

        Then I get a 401 HTTP response code
        And the X-Request-ID response header matches the request
        And the X-Correlation-ID response header matches the request
        And the response body does not contain id
        And the response body is the Empty Authorization header response

    Scenario: Attempt to retrieve a patient with an invalid authorization header
        Given I am a healthcare worker user
        And I have a header Authorization value of "Bearer abcdef123456789"

        When I retrieve a patient

        Then I get a 401 HTTP response code
        And the X-Request-ID response header matches the request
        And the X-Correlation-ID response header matches the request
        And the response body does not contain id
        And the response body is the Invalid Access Token response

    Scenario: Attempt to retrieve a patient without stating a role
        Given I am a healthcare worker user
        And I don't have a NHSD-Session-URID header

        When I retrieve a patient

        Then I get a 400 HTTP response code
        And the X-Request-ID response header matches the request
        And the X-Correlation-ID response header matches the request
        And the response body does not contain id
        And the response body is the Missing URID header response

    Scenario: Attempt to retrieve a patient with an invalid role
        Given I am a healthcare worker user
        And I have a header NHSD-Session-URID value of "invalid"

        When I retrieve a patient

        Then I get a 400 HTTP response code
        And the X-Request-ID response header matches the request
        And the X-Correlation-ID response header matches the request
        And the response body does not contain id
        And the response body is the Invalid URID header response

    Scenario: Attempt to retrieve a patient without Request ID header
        Given I am a healthcare worker user
        And I have an empty X-Request-ID header

        When I retrieve a patient

        Then I get a 400 HTTP response code
        And the response header does not contain X-Request-ID
        And the X-Correlation-ID response header matches the request
        And the response body does not contain id
        And the response body is the Empty X-Request ID response

    Scenario: Attempt to retrieve a patient with an invalid X-Request-ID
        Given I am a healthcare worker user
        And I have a header X-Request-ID value of "1234"

        When I retrieve a patient

        Then I get a 400 HTTP response code
        And the X-Request-ID response header matches the request
        And the X-Correlation-ID response header matches the request
        And the response body does not contain id
        And the response body is the Invalid X-Request ID response

    Scenario: Attempt to retrieve a patient with a missing X-Request-ID
        Given I am a healthcare worker user
        And I don't have a X-Request-ID header

        When I retrieve a patient

        Then I get a 400 HTTP response code
        And the response header does not contain X-Request-ID
        And the X-Correlation-ID response header matches the request
        And the response body does not contain id
        And the response body is the Missing X-Request ID response
