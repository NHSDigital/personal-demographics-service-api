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

