Feature: Status endpoint
    Status endpoints provide an ability to check the status of the API

    Scenario: Ping endpoint
        Given I am an unknown user

        When I hit the /_ping endpoint

        Then I get a 200 HTTP response code

    Scenario: Healthcheck endpoint
        Given I am a healthcare worker user

        When I hit the /healthcheck endpoint

        Then I get a 200 HTTP response code
