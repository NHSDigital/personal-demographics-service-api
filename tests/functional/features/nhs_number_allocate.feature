Feature: Allocate an NHS Number
	Attempt to allocate an NHS Number

	Scenario: A patient cannot allocate an NHS number
		Given I am a P9 user
		And scope added to product
		
		When I request an NHS number

		Then I get a 403 HTTP response code
		And INVALID_METHOD is at issue[0].details.coding[0].code in the response body
		And Cannot update resource without Healthcare Worker access token is at issue[0].details.coding[0].display in the response body
		And Your app has insufficient permissions to use this method. Please contact support. is at issue[0].diagnostics in the response body
	
	Scenario: An application-restricted app cannot allocate an NHS number
		Given I am an application-restricted user
		And scope added to product
		And product grants access to proxy

		When I request an NHS number

		Then I get a 403 HTTP response code
		And INVALID_METHOD is at issue[0].details.coding[0].code in the response body
		And Cannot update resource without Healthcare Worker access token is at issue[0].details.coding[0].display in the response body
		And Your app has insufficient permissions to use this method. Please contact support. is at issue[0].diagnostics in the response body

	Scenario: A healthcare worker can allocate an NHS number
		Given I am a healthcare worker user
		
		When I request an NHS number

		Then I get a 400 HTTP response code
		And UNSUPPORTED_SERVICE is at issue[0].details.coding[0].code in the response body
