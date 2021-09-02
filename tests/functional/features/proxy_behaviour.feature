Feature: General Proxy Behaviour
    As an api consumer,
    I want to get a rate limiting error from the ApplyRateLimiting shared flow
    when I trigger the spike arrest or quota limit,
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

    Scenario: App based quota is tripped
        Given I have an app with a low quota set
        When the quota is tripped
        Then I get a 429 HTTP response
        And returns a rate limit error message

    Scenario: App based rate limit is tripped
        Given I have an app with a low rate limit set
        When I make a GET request and the rate limit is tripped
        Then I get a 429 HTTP response
        And returns a rate limit error message
