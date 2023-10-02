Feature: Related Person endpoint
    Access a patient's related person

    Scenario: Retrieve a related person
        Given I am a healthcare worker
        And I have a patient with a related person

        When I retrieve their related person

        Then I get a 200 HTTP response
        And the X-Request-ID response header matches the request
        And the X-Correlation-ID response header matches the request
        And the response body contains the expected response
