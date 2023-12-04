Feature: Patient Access (Update)
	Update a PDS record as a patient

	Scenario: Patient cannot update another patient
		Given I am a P9 user
		And Scope added to product

		When I update another patient's PDS record

		Then I get a 403 HTTP response code
		And Patient cannot perform this action is at issue[0].details.coding[0].code in the response body
 
	Scenario: Patient update uses incorrect path
		Given I am a P9 user
		And Scope added to product

		When I update another patient's PDS record using an incorrect path

		Then I get a 403 HTTP response code
		And Patient cannot perform this action is at issue[0].details.coding[0].code in the response body
