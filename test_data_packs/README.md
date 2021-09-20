# PDS Test Data 

This folder contains test data patients in JSON format.

* `test patient 1`
* `test patient 2`
* `test patient 3`

You can view these JSONs [here](http://jsonviewer.stack.hu/) or by clicking on the patient you wish to view.

```
{
    "address": [
        {
            "extension": [
                {
                    "extension": [
                        {
                            "url": "type",
                            "valueCoding": {
                                "code": "PAF",
                                "system": "https://fhir.hl7.org.uk/CodeSystem/UKCore-AddressKeyType"
                            }
                        },
                        {
                            "url": "value",
                            "valueString": "20170542"
                        }
                    ],
                    "url": "https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-AddressKey"
                }
            ],
            "id": "gnpb",
            "line": [
                "EAST LODGE",
                "ROOKERY HILL",
                "ASHTEAD",
                "SURREY"
            ],
            "period": {
                "start": "2011-06-23"
            },
            "postalCode": "KT21 1JA",
            "use": "home"
        }
    ],
    "birthDate": "2009-02-15",
    "gender": "male",
    "generalPractitioner": [
        {
            "id": "dpa4",
            "identifier": {
                "period": {
                    "start": "2009-09-10"
                },
                "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                "value": "H81109"
            },
            "type": "Organization"
        }
    ],
    "id": "9449306613",
    "identifier": [
        {
            "extension": [
                {
                    "url": "https://fhir.hl7.org.uk/StructureDefinition/Extension-UKCore-NHSNumberVerificationStatus",
                    "valueCodeableConcept": {
                        "coding": [
                            {
                                "code": "01",
                                "display": "Number present and verified",
                                "system": "https://fhir.hl7.org.uk/CodeSystem/UKCore-NHSNumberVerificationStatus",
                                "version": "1.0.0"
                            }
                        ]
                    }
                }
            ],
            "system": "https://fhir.nhs.uk/Id/nhs-number",
            "value": "9449306613"
        }
    ],
    "meta": {
        "security": [
            {
                "code": "U",
                "display": "unrestricted",
                "system": "https://www.hl7.org/fhir/valueset-security-labels.html"
            }
        ],
        "versionId": "7"
    },
    "name": [
        {
            "family": "ANDERTON",
            "given": [
                "BRIAR",
                "CHADWICK"
            ],
            "id": "frbv",
            "period": {
                "start": "2010-10-11"
            },
            "prefix": [
                "MR"
            ],
            "use": "usual"
        }
    ],
    "resourceType": "Patient",
    "telecom": [
        {
            "id": "C71F3BDC",
            "period": {
                "start": "2020-07-01"
            },
            "system": "email",
            "use": "home",
            "value": "a@b.com"
        },
        {
            "id": "DE59465F",
            "period": {
                "start": "2020-07-01"
            },
            "system": "phone",
            "use": "home",
            "value": "0113554466"
        }
    ]
}
```