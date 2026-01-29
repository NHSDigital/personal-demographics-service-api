@sandbox-only
Feature: Update patient's record - OAS file examples
    The public OAS file (https://digital.nhs.uk/developer/api-catalogue/personal-demographics-service-fhir) lists a number
    of search examples and expected responses. This feature file makes sure the sandbox behaves in the same way that the
    documentation describes.

  Background:
    # auth
    * def accessToken = karate.callSingle('classpath:auth/auth-redirect.feature').accessToken
    * def requestHeaders = call read('classpath:auth/auth-headers.js')
    * configure headers = requestHeaders 
    * url baseURL
    * def nhsNumber = '9000000033'
    * path 'Patient', nhsNumber
    * method get
    * status 200
    * def originalVersion = parseInt(response.meta.versionId)  
    * header Content-Type = "application/json-patch+json"
    * header If-Match = karate.response.header('etag')
  
Scenario:  Healthcare worker can add deceased date and death notification
    * def nhsNumber = '9000000033'
    * def deceasedDate = '2020-01-01'
    * def extensionVal = 
    """
      {
        "extension": [
          {
            "url": "deathNotificationStatus",
            "valueCodeableConcept": {
              "coding": [
                {
                  "code": "1",
                  "display": "Informal - death notice received via an update from a local NHS Organisation such as GP or Trust",
                  "system": "https://fhir.hl7.org.uk/CodeSystem/UKCore-DeathNotificationStatus",
                  "version": "1.0.0"
                }
              ]
            }
          },
          {
            "url": "systemEffectiveDate",
            "valueDateTime": "2020-02-27T16:14:58+00:00"
          }
        ],
        "url": "https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-DeathNotificationStatus"
      }
    """
    * path 'Patient', nhsNumber
    * request 
     """ 
    {
      "patches": [
        { "op": "add", "path": "/deceasedDateTime", "value": "#(deceasedDate)" }, 
         {"op": "add", "path": "/extension/-", "value": "#(extensionVal)" }
    ]
    } 
    """
    * method patch
    * status 200
    * match response.id == nhsNumber
    * match response.deceasedDateTime contains deceasedDate

Scenario:  Healthcare worker can update deceased date and death notification
    * def nhsNumber = '9000000009'
    * def deceasedDate = '2010-10-23'
    * def extensionVal = 
    """
        {
            "extension": [
                {
                    "url": "deathNotificationStatus",
                    "valueCodeableConcept": {
                        "coding": [
                            {
                                "code": "1",
                                "display": "Informal - death notice received via an update from a local NHS Organisation such as GP or Trust",
                                "system": "https://fhir.hl7.org.uk/CodeSystem/UKCore-DeathNotificationStatus",
                                "version": "1.0.0"
                            }
                        ]
                    }
                },
                {
                    "url": "systemEffectiveDate",
                    "valueDateTime": "2010-10-23T16:14:58+00:00"
                }
            ],
            "url": "https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-DeathNotificationStatus"
        }
    """
    * path 'Patient', nhsNumber
    * request 
     """ 
    {
      "patches": [
        { "op": "replace", "path": "/deceasedDateTime", "value": "#(deceasedDate)" }, 
         {"op": "replace", "path": "/extension/3", "value": "#(extensionVal)" }
    ]
    } 
    """
    * method patch
    * status 200 
    * match response.id == nhsNumber
    * match response.deceasedDateTime contains deceasedDate   

Scenario:  Healthcare worker can add communication extension
    * def nhsNumber = '9000000033'
    * def extensionVal = 
    """
        {
            "url": "https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-NHSCommunication",
            "extension": [{
                    "url": "language",
                    "valueCodeableConcept": {
                        "coding": [{
                                "system": "https://fhir.hl7.org.uk/CodeSystem/UKCore-HumanLanguage",
                                "version": "1.0.0",
                                "code": "q4",
                                "display": "British Sign Language"
                            }
                        ]
                    }
                }, {
                    "url": "interpreterRequired",
                    "valueBoolean": true
                }
            ]
        }
    """
    * path 'Patient', nhsNumber
    * request 
     """ 
    {
      "patches": [ 
         {"op": "add", "path": "/extension/-", "value": "#(extensionVal)" }
    ]
    } 
    """
    * method patch
    * status 200  
    * match response.extension contains extensionVal 

Scenario:  Healthcare worker can update communication extension
    * def nhsNumber = '9000000009'
    * def extensionVal = 
    """
        {
    "url": "https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-NHSCommunication",
    "extension": [{
            "url": "language",
            "valueCodeableConcept": {
                "coding": [{
                        "system": "https://fhir.hl7.org.uk/CodeSystem/UKCore-HumanLanguage",
                        "version": "1.0.0",
                        "code": "q3",
                        "display": "Australian Sign Language"
                    }
                ]
            }
        }, {
            "url": "interpreterRequired",
            "valueBoolean": false
        }
    ]
      }
    """
    * path 'Patient', nhsNumber
    * request 
     """ 
    {
      "patches": [
         {"op": "replace", "path": "/extension/4", "value": "#(extensionVal)" }
    ]
    } 
    """
    * method patch
    * status 200
    * match response.extension contains extensionVal    
    
Scenario:  Healthcare worker can update communication single itesm
    * def nhsNumber = '9000000009'
    * def extensionVal = 
    """
        {
            "url": "language",
            "valueCodeableConcept": {
                "coding": [{
                        "system": "https://fhir.hl7.org.uk/CodeSystem/UKCore-HumanLanguage",
                        "version": "1.0.0",
                        "code": "q3",
                        "display": "Australian Sign Language"
                    }
                ]
            }
        }
    """
    * path 'Patient', nhsNumber
    * request 
     """ 
    {
      "patches": [
         {"op": "replace", "path": "/extension/4/extension/0", "value": "#(extensionVal)" }
    ]
    } 
    """
    * method patch
    * status 200
    * match response.extension[4].extension[0] contains extensionVal     
  
Scenario:  Healthcare worker can remove Remove Communication
    * def nhsNumber = '9000000009'
    * def extensionURL = "https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-NHSCommunication"
    * path 'Patient', nhsNumber
    * request 
     """ 
        {
            "patches": [
              { 
                "op": "test",
                "path": "/extension/4/url",
                "value": "#(extensionURL)"
              },
              { 
                "op": "remove",
                "path": "/extension/4"
              }
            ]
        }
    """
    * method patch
    * status 200
    * match response.extension !contains extensionURL      

Scenario:  Healthcare worker can replace a Single Contact Preference
    * def nhsNumber = '9000000009'
    * def extensionVal = 
    """
        {
            "url": "PreferredContactMethod",
            "valueCodeableConcept": {
                "coding": [{
                        "code": "3",
                        "display": "Telephone",
                        "system": "https://fhir.hl7.org.uk/ValueSet/UKCore-PreferredContactMethod"
                    }
                ]
            }
          }

    """
    * path 'Patient', nhsNumber
    * request 
     """ 
        {
            "patches": [
                {
        "op": "replace",
        "path": "/extension/5/extension/1",
        "value":  "#(extensionVal)"
            }
            ]
        }
    """
    * method patch
    * status 200
    * match response.extension[5].extension[1] contains extensionVal     
    
Scenario:  Healthcare worker can replace and remove Contact Preference
    * def nhsNumber = '9000000009'
    * def extensionVal = 
    """
        {
          "url": "https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-ContactPreference",
          "extension": [
          {
            "url": "PreferredContactMethod",
            "valueCodeableConcept": {
                "coding": [{
                        "code": "7",
                        "display": "Sign language",
                        "system": "https://fhir.hl7.org.uk/ValueSet/UKCore-PreferredContactMethod"
                    }
                ]
            }
          },
          {
            "url": "PreferredContactTimes",
            "valueString": "13:00"
          }
        ]
      }
    """
    * path 'Patient', nhsNumber
    * request 
     """ 
        {
            "patches": [
                {
            "op": "replace",
            "path": "/extension/5",
            "value": "#(extensionVal)"
            }
            ]
        }
    """
    * method patch
    * status 200
    * match response.extension[5] contains extensionVal
    * path 'Patient', nhsNumber
    * method get
    * status 200
    * configure headers = call read('classpath:auth/auth-headers.js')     
    * header Content-Type = "application/json-patch+json"
    * header If-Match = karate.response.header('etag')  
    * path 'Patient', nhsNumber
    * request 
     """ 
        {
            "patches": [
                {
            "op": "remove",
            "path": "/extension/5",
            }
            ]
        }
    """
    * method patch
    * status 200
    * match response.extension !contains extensionVal 
    
Scenario:  Healthcare worker can remove Single Contact Preference
    * def nhsNumber = '9000000009'
    * def firstExtensionURL = "PreferredWrittenCommunicationFormat"
    * path 'Patient', nhsNumber
    * request 
     """ 
        {
            "patches": [
              { 
                "op": "test",
                "path": "/extension/5/extension/0/url",
                "value": "#(firstExtensionURL)"
              },
              { 
                "op": "remove",
                "path": "/extension/5/extension/2"
              }
            ]
        }
    """
    * method patch
    * status 200
    * def extensionsIn5thExtension = response.extension[5].extension.length
    * if (extensionsIn5thExtension > 2) { karate.fail('Single Contact Preference not been removed from /extension/5/extension/2.')}
    * match response.extension[5].url == "https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-ContactPreference"
    * match response.extension[5].extension[0].url == firstExtensionURL
    * match response.extension[5].extension[1].url == "PreferredContactMethod"
  