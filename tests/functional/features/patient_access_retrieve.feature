Feature: Patient Access (Retrieve)
	Retrieve a PDS record as a patient

	Scenario: Patient can retrieve self
		Given I am a P9 user
		And scope added to product
		
		When I retrieve my details

		Then I get a 200 HTTP response code

	Scenario: Patient cannot retrieve self with P5 authorisation level
		Given I am a P5 user with the NHS number linked to an account
		
		When I sign in using NHS login

		Then I get a 401 HTTP response code
		And unauthorized_client is at error in the response body
		And you have tried to request authorization but your application is not configured to use this authorization grant type is at error_description in the response body
	
	Scenario: Patient cannot retrieve self with P0 authorisation level
		Given I am a P0 user with the NHS number linked to an account
		
		When I sign in using NHS login

		Then I get a 401 HTTP response code
		And unauthorized_client is at error in the response body
		And you have tried to request authorization but your application is not configured to use this authorization grant type is at error_description in the response body

	Scenario: Patient cannot retrieve another patient
		Given I am a P9 user
		And scope added to product
		And I have another patient's NHS number
		
		When I retrieve a patient

		Then I get a 403 HTTP response code
		And ACCESS_DENIED is at issue[0].details.coding[0].code in the response body
		And Patient cannot perform this action is at issue[0].details.coding[0].display in the response body

	Scenario: Patient attempts to search for a patient
		Given I am a P9 user
		And scope added to product
		
		When I search for a patient's PDS record

		Then I get a 403 HTTP response code
		And ACCESS_DENIED is at issue[0].details.coding[0].code in the response body
		And Patient cannot perform this action is at issue[0].details.coding[0].display in the response body

	Scenario: Patient cannot retrieve their record with an expired token
		Given I am a P9 user
		And scope added to product
		And I have an expired access token

		When I retrieve my details

		Then I get a 401 HTTP response code
		And ACCESS_DENIED is at issue[0].details.coding[0].code in the response body
		And Access Token expired is at issue[0].diagnostics in the response body

	Scenario: Patient can retrieve their record with a refreshed token
		Given I am a P9 user
		And scope added to product
		And I have a refreshed access token

		When I retrieve my details

		Then I get a 200 HTTP response code