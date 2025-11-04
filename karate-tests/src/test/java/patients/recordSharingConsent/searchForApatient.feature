@no-oas
Feature: Search for a patient(Healthcare worker access)- nhs record sharing consent

Background:
    * def utils = call read('classpath:helpers/utils.feature')
    * url baseURL

Scenario:Search for a patient using parameters response should not include consent sharing details
    # auth
    * def accessToken = karate.call('classpath:auth/auth-redirect.feature', {clientID: karate.get('recordSharingConsentClientID'), clientSecret:karate.get('recordSharingConsentClientSecret')}).accessToken
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders 
    * def searchParams =
        """
        { family: "SEGAR", gender: "female", birthdate: "1995-07-03"}
        """
    * call read('classpath:patients/common/getPatient.feature@searchForAPatient') searchParams
    * match response.entry[0].resource.id == "9733163767"
    * match response.entry[0].resource.extension == '#notpresent'

Scenario:Search for a patient using parameters response should not include consent sharing details for default test app
    # auth
    * def accessToken = karate.call('classpath:auth/auth-redirect.feature').accessToken
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders 
    * def searchParams =
        """
        { family: "SUTTER", gender: "female", birthdate: "1987-02-05" }
        """
    * call read('classpath:patients/common/getPatient.feature@searchForAPatient') searchParams
    * path "Patient"
    * match response.entry[0].resource.id == "9733163759"
    * match response.entry[0].resource.extension == '#notpresent' 