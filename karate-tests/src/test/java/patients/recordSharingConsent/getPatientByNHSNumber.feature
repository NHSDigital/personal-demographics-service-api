@no-oas
Feature: Get a patient - nhs record sharing consent

Background:
    * def utils = call read('classpath:helpers/utils.feature')
    # auth
    * url baseURL
    * def consentSharingToken =
    """
    function() {
    var result = karate.call('classpath:auth/auth-redirect.feature', {
        clientID: karate.get('confidentialRemovalReasonsClientID'),
        clientSecret: karate.get('confidentialRemovalReasonsClientSecret')
    });
    return result.accessToken
    }
    """
Scenario: Get a patient details- RemovalReasonExitCode should be Armed Forces (notified by Armed Forces) AFN
    * def accessToken = consentSharingToken()
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders  
    * path 'Patient', removedArmedForcesNhsNumber
    * method get
    * status 200
    * match response.extension[0].extension[0].valueCodeableConcept.coding[0].code == "AFN"
    * match response.extension[0].extension[0].valueCodeableConcept.coding[0].display == "Armed Forces (notified by Armed Forces)"
    * match response.extension[0].url == removalURL
    * match responseHeaders['Nhse-Pds-Custom-Attributes'] == '#notpresent'
  
Scenario: Response should not include consent sharing extension when default test app include the return-nhs-record-sharing-consent custom attribute header
    * def accessToken = karate.call('classpath:auth/auth-redirect.feature').accessToken
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * def customAttributeHeader = {'Nhse-Pds-Custom-Attributes': '{"return-nhs-record-sharing-consent":"true"}'}
    * def mergeHeaders = karate.merge(requestHeaders, customAttributeHeader)
    * configure headers = mergeHeaders 
    * def accessToken = karate.callSingle('classpath:auth/auth-redirect.feature').accessToken
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders  
    * path 'Patient', removedArmedForcesNhsNumber
    * method get
    * status 200
    * match response.extension[0].extension[0].valueCodeableConcept.coding[0].code == "ORR"
    * match response.extension[0].extension[0].valueCodeableConcept.coding[0].display == "Other Reason"
    * match response.extension[0].url == removalURL  
    * match responseHeaders['Nhse-Pds-Custom-Attributes'] == '#notpresent'  