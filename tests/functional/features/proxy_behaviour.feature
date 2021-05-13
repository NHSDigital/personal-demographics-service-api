Feature: General Proxy Behaviour
    As an api consumer,
    I want to get a rate limit error when I trigger the spike arrest policy,
    So that I get correct error messages when I send too many requests.

    Scenario: API Proxy rate limit tripped
        Given I have a proxy with a low rate limit set
        When the rate limit is tripped
        Then I get a 429 HTTP response
        And returns a rate limit error message

    Scenario: API quota is tripped
        Given I have a proxy with a low quota set
        When the quota is tripped
        Then I get a 429 HTTP response
        And returns a rate limit error message

    Scenario: Rate limit is not tripped for normal 
        Given I have a proxy
        Given the product has a default quota and rate limit set
        When I send numerous requests
        Then I do not trip the rate limit