@no-oas
Feature: Get a patient(patient access)- confidential reasons for removal

Background:
    * def utils = call read('classpath:helpers/utils.feature')
    # auth
    * url baseURL
    * def removalURL = "https://fhir.nhs.uk/StructureDefinition/Extension-PDS-RemovalFromRegistration"
      
Scenario: Get a patient details- RemovalReasonExitCode should be Armed Forces (notified by Armed Forces) AFN
    * def nhsNumber = '9733162981'
    * def accessToken = karate.call('classpath:auth/auth-redirect.feature', {clientID: karate.get('confidentialRemovalReasonsClientID'), clientSecret:karate.get('confidentialRemovalReasonsClientSecret')}).accessToken
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders  
    * path 'Patient', nhsNumber
    * method get
    * status 200
    * match response.extension[0].extension[0].valueCodeableConcept.coding[0].code == "AFN"
    * match response.extension[0].extension[0].valueCodeableConcept.coding[0].display == "Armed Forces (notified by Armed Forces)"
    * match response.extension[0].url == removalURL
    * match responseHeaders['Nhse-Pds-Custom-Attributes'] == '#notpresent'
Scenario: Get a patient details- RemovalReasonExitCode should be Services dependant (notified by SMO) SDN
    * def nhsNumber = '9733163023'
    * def accessToken = karate.call('classpath:auth/auth-redirect.feature', {clientID: karate.get('confidentialRemovalReasonsClientID'), clientSecret:karate.get('confidentialRemovalReasonsClientSecret')}).accessToken
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders  
    * path 'Patient', nhsNumber
    * method get
    * status 200
    * match response.extension[0].extension[0].valueCodeableConcept.coding[0].code == "SDN"
    * match response.extension[0].extension[0].valueCodeableConcept.coding[0].display == "Services dependant (notified by SMO)"
    * match response.extension[0].url == removalURL
Scenario: Get a patient details- RemovalReasonExitCode should be SCT - Transferred to Scotland
    * def nhsNumber = '9733163058'
    * def accessToken = karate.call('classpath:auth/auth-redirect.feature', {clientID: karate.get('confidentialRemovalReasonsClientID'), clientSecret:karate.get('confidentialRemovalReasonsClientSecret')}).accessToken
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders  
    * path 'Patient', nhsNumber
    * method get
    * status 200
    * match response.extension[0].extension[0].valueCodeableConcept.coding[0].code == "SCT"
    * match response.extension[0].extension[0].valueCodeableConcept.coding[0].display == "Transferred to Scotland"
    * match response.extension[0].url == removalURL    
Scenario: Get a patient details- RemovalReasonExitCode should be converted from 'Logical deletion' (LDN) to 'Other Reason' (ORR)"
    * def nhsNumber = '9733163015'
    * def accessToken = karate.call('classpath:auth/auth-redirect.feature', {clientID: karate.get('confidentialRemovalReasonsClientID'), clientSecret:karate.get('confidentialRemovalReasonsClientSecret')}).accessToken
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders  
    * path 'Patient', nhsNumber
    * method get
    * status 200
    * match response.extension[0].extension[0].valueCodeableConcept.coding[0].code == "ORR"
    * match response.extension[0].extension[0].valueCodeableConcept.coding[0].display == "Other Reason"
    * match response.extension[0].url == removalURL 
    
Scenario: Get a patient details- RemovalReasonExitCode should be converted from Armed Forces (notified by Armed Forces) AFN to 'Other Reason' (ORR)" 
            for non screening users
    * def nhsNumber = '9733162981'
    * def accessToken = karate.callSingle('classpath:auth/auth-redirect.feature').accessToken
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders  
    * path 'Patient', nhsNumber
    * method get
    * status 200
    * match response.extension[0].extension[0].valueCodeableConcept.coding[0].code == "ORR"
    * match response.extension[0].extension[0].valueCodeableConcept.coding[0].display == "Other Reason"
    * match response.extension[0].url == removalURL    

Scenario: Response should not include confidential reasons when default test app include the confidential reasons custom attribute
    * def accessToken = karate.call('classpath:auth/auth-redirect.feature').accessToken
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * def customAttributeHeader = {'Nhse-Pds-Custom-Attributes': '{"return-confidential-reason-for-removal":"true"}'}
    * def mergeHeaders = karate.merge(requestHeaders, customAttributeHeader)
    * configure headers = mergeHeaders 
    * def nhsNumber = '9733162981'
    * def accessToken = karate.callSingle('classpath:auth/auth-redirect.feature').accessToken
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders  
    * path 'Patient', nhsNumber
    * method get
    * status 200
    * match response.extension[0].extension[0].valueCodeableConcept.coding[0].code == "ORR"
    * match response.extension[0].extension[0].valueCodeableConcept.coding[0].display == "Other Reason"
    * match response.extension[0].url == removalURL  
    * match responseHeaders['Nhse-Pds-Custom-Attributes'] == '#notpresent'    