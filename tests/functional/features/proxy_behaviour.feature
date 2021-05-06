Feature: General Proxy Behaviour
    As an api consumer,
    I want to get a rate limit error when I trigger the spike arrest policy,
    So that I get correct error messages when I send too many requests.

    Scenario: API Proxy rate limit tripped
        Given I have a proxy with a low rate limit set
        When I make a GET request and the rate limit is tripped
        Then I get a 429 HTTP response
        And returns a rate limit error message

    Scenario: API quota is tripped
        Given I have a proxy with a low quota set
        When the quota is tripped
        Then I get a 429 HTTP response
        And returns a rate limit error message

    Scenario: The rate limit tripped for PATCH requests
        Given I have a proxy with a low rate limit set
        When I make a PATCH request and the rate limit is tripped
        Then I get a 429 HTTP response
        And returns a rate limit error message