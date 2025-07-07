@no-oas 
Feature: Get a patient - nhs record sharing consent

Background:
    * def utils = call read('classpath:helpers/utils.feature')
    * def consentURL = "https://hl7.org/fhir/R4/consent.html"
    # auth
    * url baseURL
    * def consentSharingToken =
    """
    function() {
    var result = karate.call('classpath:auth/auth-redirect.feature', {
        clientID: karate.get('recordSharingConsentClientID'),
        clientSecret: karate.get('recordSharingConsentClientSecret')
    });
    return result.accessToken
    }
    """
Scenario: Get a patient details- record has express consent value(1)
    * def expressConsentNhsNumber = "9733163767"
    * def accessToken = consentSharingToken()
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders  
    * path 'Patient', expressConsentNhsNumber
    * method get
    * status 200
    * match response.extension[0].extension[0].valueCodeableConcept.coding[0].code == "4"
    * match response.extension[0].extension[0].valueCodeableConcept.coding[0].display == "ncrs"
    * match response.extension[0].extension[0].url == "consentType"
    * match response.extension[0].extension[1].valueCodeableConcept.coding[0].code == "1"
    * match response.extension[0].extension[1].valueCodeableConcept.coding[0].display == "consent"
    * match response.extension[0].extension[1].url == "consentValue"
    * match response.extension[0].url == consentURL
    * match responseHeaders['Nhse-Pds-Custom-Attributes'] == '#notpresent'

Scenario: Get a patient details- record has express dissent value(2)
    * def expressDissentNhsNumber = "9733163759"
    * def accessToken = consentSharingToken()
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders  
    * path 'Patient', expressDissentNhsNumber
    * method get
    * status 200
    * match response.extension[0].extension[0].valueCodeableConcept.coding[0].code == "4"
    * match response.extension[0].extension[0].valueCodeableConcept.coding[0].display == "ncrs"
    * match response.extension[0].extension[0].url == "consentType"
    * match response.extension[0].extension[1].valueCodeableConcept.coding[0].code == "2"
    * match response.extension[0].extension[1].valueCodeableConcept.coding[0].display == "dissent"
    * match response.extension[0].extension[1].url == "consentValue"
    * match response.extension[0].url == consentURL
    * match responseHeaders['Nhse-Pds-Custom-Attributes'] == '#notpresent'    
  
Scenario: Get a patient details- record has unknown ConsentValue(3)
    * def nhsNumber = "9733163775"
    * def accessToken = consentSharingToken()
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders  
    * path 'Patient', nhsNumber
    * method get
    * status 200
    * def hasConsentType = karate.filter(response.extension, x => x.url == 'consentType')
    * match hasConsentType == []

Scenario: Get a patient details- record has call centre callback ConsentValue(5)
    * def nhsNumber = "9733163740"
    * def accessToken = consentSharingToken()
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders  
    * path 'Patient', nhsNumber
    * method get
    * status 200
    * def hasConsentType = karate.filter(response.extension, x => x.url == 'consentType')
    * match hasConsentType == []  
  
Scenario: Response should not include consent sharing extension when default test app include the return-nhs-record-sharing-consent custom attribute header
    * def nhsNumber = "9733163767"
    * def accessToken = karate.call('classpath:auth/auth-redirect.feature').accessToken
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * def customAttributeHeader = {'Nhse-Pds-Custom-Attributes': '{"return-nhs-record-sharing-consent":"true"}'}
    * def mergeHeaders = karate.merge(requestHeaders, customAttributeHeader)
    * configure headers = mergeHeaders  
    * path 'Patient', nhsNumber
    * method get
    * status 200
    * def hasConsentType = karate.filter(response.extension, x => x.url == 'consentType')
    * match hasConsentType == [] 
    * match responseHeaders['Nhse-Pds-Custom-Attributes'] == '#notpresent' 

Scenario: Get a patient details- App has multiple custom attributes(return-empty-address-lines,return-confidential-reason-for-removal,return-nhs-record-sharing-consent)
    * def nhsNumber = "9733163082"
    * def accessToken = consentSharingToken()
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders  
    * path 'Patient', nhsNumber
    * method get
    * status 200
    # consent sharing validations
    * match response.extension[1].extension[0].valueCodeableConcept.coding[0].code == "4"
    * match response.extension[1].extension[0].valueCodeableConcept.coding[0].display == "ncrs"
    * match response.extension[1].extension[0].url == "consentType"
    * match response.extension[1].extension[1].valueCodeableConcept.coding[0].code == "1"
    * match response.extension[1].extension[1].valueCodeableConcept.coding[0].display == "consent"
    # RFR validations
    * match response.extension[0].extension[0].valueCodeableConcept.coding[0].code == "AFN"
    * match response.extension[0].extension[0].valueCodeableConcept.coding[0].display == "Armed Forces (notified by Armed Forces)"  
    # Empty address lines validations
    * def addresses = response.address
    * match utils.checkNullsHaveExtensions(addresses) == true
    * match responseHeaders['Nhse-Pds-Custom-Attributes'] == '#notpresent'