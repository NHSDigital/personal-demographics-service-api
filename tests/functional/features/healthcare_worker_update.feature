Feature: Healthcare Worker Access (Update)
    Update a PDS record as a healthcare worker
    
    Scenario: Update patient
        Given I am a healthcare worker
        And I have a patient's record to update
        And I wish to update the patient's gender

        When I update the patient's PDS record

        Then I get a 200 HTTP response
        And the response body contains the patient's new gender
        And the response body contains the record's new version number

    Scenario: Update patient using deprecated respond-async still returns 200
        Given I am a healthcare worker
        And I have a patient's record to update
        And I wish to update the patient's gender
        And I have a header Prefer value of "respond-async"

        When I update the patient's PDS record

        Then I get a 200 HTTP response
        And the response body contains the patient's new gender
        And the response body contains the record's new version number

    Scenario: Update patient with invalid wait header still updates
        Given I am a healthcare worker
        And I have a patient's record to update
        And I wish to update the patient's gender
        And I have a header X-Sync-Wait value of "invalid"

        When I update the patient's PDS record

        Then I get a 200 HTTP response
        And the response body contains the patient's new gender
        And the response body contains the record's new version number

    Scenario: Update patient with low wait header
        Given I am a healthcare worker
        And I have a patient's record to update
        And I wish to update the patient's gender
        And I have a header X-Sync-Wait value of "0.25"

        When I update the patient's PDS record

        Then I get a 503 HTTP response

    Scenario: Update patient with missing Authorization header
        Given I am a healthcare worker
        And I have a patient's record to update
        And I wish to update the patient's gender
        And I don't have a Authorization header

        When I update the patient's PDS record

        Then I get a 401 HTTP response
        And the X-Request-ID response header matches the request
        And the X-Correlation-ID response header matches the request
        And the response body is the Missing Authorization header response

    Scenario: Update patient with an empty authorization header
        Given I am a healthcare worker
        And I have a patient's record to update
        And I wish to update the patient's gender
        And I have an empty Authorization header

        When I update the patient's PDS record

        Then I get a 401 HTTP response
        And the X-Request-ID response header matches the request
        And the X-Correlation-ID response header matches the request
        And the response body is the Empty Authorization header response

    Scenario: Update patient with an invalid authorization header
        Given I am a healthcare worker
        And I have a patient's record to update
        And I wish to update the patient's gender
        And I have a header Authorization value of "Bearer abcdef123456789"

        When I update the patient's PDS record

        Then I get a 401 HTTP response
        And the X-Request-ID response header matches the request
        And the X-Correlation-ID response header matches the request
        And the response body is the Invalid Access Token response

    Scenario: Update patient with an empty Request ID header
        Given I am a healthcare worker
        And I have a patient's record to update
        And I wish to update the patient's gender
        And I have an empty X-Request-ID header

        When I update the patient's PDS record

        Then I get a 400 HTTP response
        And the response header does not contain X-Request-ID
        And the X-Correlation-ID response header matches the request
        And the response body is the Empty X-Request ID response

    Scenario: Update patient with an invalid X-Request-ID
        Given I am a healthcare worker
        And I have a patient's record to update
        And I wish to update the patient's gender
        And I have a header X-Request-ID value of "1234"

        When I update the patient's PDS record

        Then I get a 400 HTTP response
        And the X-Request-ID response header matches the request
        And the X-Correlation-ID response header matches the request
        And the response body is the Invalid X-Request ID response

    Scenario: Update patient with a missing X-Request-ID
        Given I am a healthcare worker
        And I have a patient's record to update
        And I wish to update the patient's gender
        And I don't have a X-Request-ID header

        When I update the patient's PDS record

        Then I get a 412 HTTP response
        And the response header does not contain X-Request-ID
        And the X-Correlation-ID response header matches the request
        And the response body is the Missing X-Request ID response