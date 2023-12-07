Feature: Patient Access (Retrieve)
	Retrieve a PDS record as a patient

	Scenario: Patient can retrieve self
		Given I am a P9 user
		And scope added to product
		
		When I retrieve my details

		Then I get a 200 HTTP response code

	Scenario: Patient cannot retrieve another patient
		Given I am a P9 user
		And I have another patient's NHS number
		And scope added to product
		
		When I retrieve a patient

		Then I get a 403 HTTP response code
		And ACCESS_DENIED is at issue[0].details.coding[0].code in the response body
		And Patient cannot perform this action is at issue[0].details.coding[0].display in the response body

	Scenario: Patient retrieve uses incorrect path
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