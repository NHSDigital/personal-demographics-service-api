Feature: Sync-wrap failure modes
    As an api consumer,
    I want to get helpful error messages when my request times out,
    So that I respond correctly to sync-wrap side-effects.

    Scenario: When I accidentally set the X-Sync-Wait header to a low value it should time out
        Given I have a low sync-wrap timeout
        When I send a request
        Then I get a 503 HTTP response
        And returns a helpful error message

    Scenario: The rate limit is tripped through a synchronous request
        Given I have a proxy with a low rate limit set
        Given I have a valid PATCH request
        When the rate limit is tripped
        Then I get a 429 HTTP response
        And returns a rate limit error message

    Scenario: The rate limit is tripped during sync-wrap polling
        Given I have a proxy with a low rate limit set
        Given I have a valid PATCH request
        When the rate limit is tripped with sync-wrap polling
        Then I get a 503 HTTP response
        And returns a helpful error message

    Scenario: The rate limit is tripped when POSTing new Patients (>1tps)
        Given I have a proxy with a low rate limit set
        When the rate limit is tripped with sync-wrap polling the create Patient endpoint
        Then I get a 429 HTTP response
        And returns a rate limit error message
