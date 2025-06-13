Feature: Remove patient details
    
  Scenario: Remove place of birth

    * url baseURL
    * def placeOfBirthNhsNumber = '5900077810'
    * def placeOBirthUrl = 'http://hl7.org/fhir/StructureDefinition/patient-birthPlace'
   
    * path 'Patient', placeOfBirthNhsNumber
    * method get
    * status 200
     
    # remove place of birth details
    * configure headers = call read('classpath:auth/auth-headers.js') 
    * header Content-Type = "application/json-patch+json"
    * header If-Match = karate.response.header('etag')

    * def pobIndex = response.extension.findIndex(x => x.url == placeOBirthUrl)
    * def pobPath =  "/extension/" + pobIndex
    * path 'Patient', placeOfBirthNhsNumber
    * request 
    """
      {
        "patches": [
          {
            "op": "test",
            "path": "#(pobPath)",
            "value": "#(pobDetails)"     
          },
          {
           "op": "remove",
            "path": "#(pobPath)" 
          }
        ]
      }
      """ 
    * method patch
    * status 200