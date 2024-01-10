Feature: Related Person endpoint
    Access a patient's related person

    Scenario: Retrieve a related person
        Given I am a healthcare worker user
        And I have a patient with a related person

        When I retrieve their related person

        Then I get a 200 HTTP response code
        And the X-Request-ID response header matches the request
        And the X-Correlation-ID response header matches the request
        And the response body contains the expected response

    Scenario: Patient can retrieve a single related person
        Given I am a P9_WITH_RELATED_PERSON user
        And scope added to product
        And I am a patient with a related person

        When I retrieve my related person

        Then I get a 200 HTTP response code

    Scenario: Patient can't retrieve a related person for another patient
        Given I am a P9_WITH_RELATED_PERSON user
        And scope added to product

        When I retrieve another patient's related person

        Then I get a 403 HTTP response code