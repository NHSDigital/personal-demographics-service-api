from ..configuration.config import SPINE_HOSTNAME

RESPONSES = {
    "Missing Authorization header": {
        "resourceType": "OperationOutcome",
        "issue": [
            {
                "severity": "error",
                "code": "forbidden",
                "details": {
                    "coding": [
                        {
                            "system": "https://fhir.nhs.uk/R4/CodeSystem/Spine-ErrorOrWarningCode",
                            "version": "1",
                            "code": "ACCESS_DENIED",
                            "display": "Access Denied - Unauthorised"
                        }
                    ]
                },
                "diagnostics": "Missing Authorization header"
            }
        ]
    },
    "Empty Authorization header": {
        "resourceType": "OperationOutcome",
        "issue": [
            {
                "severity": "error",
                "code": "forbidden",
                "details": {
                    "coding": [
                        {
                            "system": "https://fhir.nhs.uk/R4/CodeSystem/Spine-ErrorOrWarningCode",
                            "version": "1",
                            "code": "ACCESS_DENIED",
                            "display": "Access Denied - Unauthorised"
                        }
                    ]
                },
                "diagnostics": "Empty Authorization header"
            }
        ]
    },
    "Invalid Access Token": {
        "resourceType": "OperationOutcome",
        "issue": [
            {
                "severity": "error",
                "code": "forbidden",
                "details": {
                    "coding": [
                        {
                            "system": "https://fhir.nhs.uk/R4/CodeSystem/Spine-ErrorOrWarningCode",
                            "version": "1",
                            "code": "ACCESS_DENIED",
                            "display": "Access Denied - Unauthorised"
                        }
                    ]
                },
                "diagnostics": "Invalid Access Token"
            }
        ]
    },
    "Missing URID header": {
        "resourceType": "OperationOutcome",
        "issue": [
            {
                "severity": "error",
                "code": "value",
                "details": {
                    "coding": [
                        {
                            "system": "https://fhir.nhs.uk/R4/CodeSystem/Spine-ErrorOrWarningCode",
                            "version": "1",
                            "code": "INVALID_VALUE",
                            "display": "Provided value is invalid"
                        }
                    ]
                },
                "diagnostics": ("Invalid value - '' in header 'NHSD-Session-URID'. Refer to the guidance "
                                "for this header in our API Specification "
                                "https://digital.nhs.uk/developer/api-catalogue/personal-demographics-service-fhir")
            }
        ]
    },
    "Invalid URID header": {
        "resourceType": "OperationOutcome",
        "issue": [
            {
                "severity": "error",
                "code": "value",
                "details": {
                    "coding": [
                        {
                            "system": "https://fhir.nhs.uk/R4/CodeSystem/Spine-ErrorOrWarningCode",
                            "version": "1",
                            "code": "INVALID_VALUE",
                            "display": "Provided value is invalid"
                        }
                    ]
                },
                "diagnostics": ("Invalid value - 'invalid' in header 'NHSD-Session-URID'. "
                                "Refer to the guidance for this header in our API Specification "
                                "https://digital.nhs.uk/developer/api-catalogue/personal-demographics-service-fhir")
            }
        ]
    },
    "Empty X-Request ID": {
        "resourceType": "OperationOutcome",
        "issue": [
            {
                "severity": "error",
                "code": "value",
                "details": {
                    "coding": [
                        {
                            "system": "https://fhir.nhs.uk/R4/CodeSystem/Spine-ErrorOrWarningCode",
                            "version": "1",
                            "code": "INVALID_VALUE",
                            "display": "Provided value is invalid"
                        }
                    ]
                },
                "diagnostics": "Invalid value - '' in header 'X-Request-ID'"
            }
        ]
    },
    "Invalid X-Request ID": {
        "resourceType": "OperationOutcome",
        "issue": [
            {
                "severity": "error",
                "code": "value",
                "details": {
                    "coding": [
                        {
                            "system": "https://fhir.nhs.uk/R4/CodeSystem/Spine-ErrorOrWarningCode",
                            "version": "1",
                            "code": "INVALID_VALUE",
                            "display": "Provided value is invalid"
                        }
                    ]
                },
                "diagnostics": "Invalid value - '1234' in header 'X-Request-ID'"
            }
        ]
    },
    "Missing X-Request ID": {
        "resourceType": "OperationOutcome",
        "issue": [
            {
                "severity": "error",
                "code": "structure",
                "details": {
                    "coding": [
                        {
                            "system": "https://fhir.nhs.uk/R4/CodeSystem/Spine-ErrorOrWarningCode",
                            "version": "1",
                            "code": "PRECONDITION_FAILED",
                            "display": "Required condition was not fulfilled"
                        }
                    ]
                },
                "diagnostics": ("Invalid request with error - "
                                "X-Request-ID header must be supplied to access this resource")
            }
        ]
    },
    "Too Many Matches": {
        "issue": [
            {
                "code": "multiple-matches",
                "details": {
                    "coding": [
                        {
                            "code": "TOO_MANY_MATCHES",
                            "display": "Too Many Matches",
                            "system": "https://fhir.nhs.uk/R4/CodeSystem/Spine-ErrorOrWarningCode",
                            "version": "1"
                        }
                    ]
                },
                "severity": "information"
            }
        ],
        "resourceType": "OperationOutcome"
    },
    "Related person": {
        "entry": [
            {
                "fullUrl": f"{SPINE_HOSTNAME}/personal-demographics/FHIR/R4/Patient/9693633679/RelatedPerson/qWyGt",
                "resource": {
                    "active": True,
                    "id": "qWyGt",
                    "patient": {
                        "identifier": {
                            "system": "https://beta.api.digital.nhs.uk",
                            "value": "9693633687"
                        },
                        "reference": "https://beta.api.digital.nhs.uk/Patient/9693633687",
                        "type": "Patient"
                    },
                    "relationship": [
                        {
                            "coding": [
                                {
                                    "code": "SPS",
                                    "display": "spouse",
                                    "system": "http://hl7.org/fhir/ValueSet/relatedperson-relationshiptype"
                                },
                                {
                                    "code": "Personal",
                                    "display": "Personal relationship with the patient",
                                    "system": "https://fhir.nhs.uk/R4/CodeSystem/UKCore-AdditionalRelatedPersonRole"
                                },
                                {
                                    "code": "N",
                                    "display": "Next-of-Kin",
                                    "system": "http://hl7.org/fhir/ValueSet/relatedperson-relationshiptype"
                                }
                            ]
                        }
                    ],
                    "resourceType": "RelatedPerson"
                }
            }
        ],
        "resourceType": "Bundle",
        "total": 1,
        "type": "searchset"
    }
}
