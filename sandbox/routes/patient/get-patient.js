const fs = require('fs')
const Boom = require('boom')
const fhirHelper = require('../../helpers/fhir-helper')
const nhsNumberHelper = require('../../helpers/nhs-number-helper')
const dateValidator = require('../../validators/date-validator')

const EXAMPLE_PATIENT_SMITH = JSON.parse(fs.readFileSync('mocks/Patient-Jane-Smith.json'))
const EXAMPLE_PATIENT_SMYTHE = JSON.parse(fs.readFileSync('mocks/Patient-Jayne-Smyth.json'))


module.exports = [
    /* Patient Search
        Behaviour Implemented:
         * Provide ?9000000009: recieve example patient record as search result
    */
    {
        method: 'GET',
        path: '/Patient/{nhsNumber}',
        handler: (request, h) => {
            nhsNumberHelper.checkNhsNumber(request)
            return fhirHelper.createFhirResponse(h, EXAMPLE_PATIENT_SMITH)
        }
    },

    /* Patient search
        Behaviour implemented:
         * Provide no recognised search params: 400 + Appropriate error
         * Provide improperly-specified birthdate/death-date param: 400 + Appropriate error
         * Provide *some* search params: Empty search response
         * Provide ?birthdate=2010-10-22&family=Smith&given=Jane&gender=female: receive example patient as search result
    */
    {
        method: 'GET',
        path: '/Patient',
        handler: (request) => {
            
            // TODO: Spilt down methods into seperate files

            // TODO: This can be provided to a PatientSearcher to use to implement a more
            // 'proper' search
            const searchMap = {
                "_exact-match": true,
                "_history": true,
                "_fuzzy-match": true,
                "_max-results": true,
                family: '$.name[?(@.use="usual")].family', // Usual family name
                given: true,
                gender: true,
                birthdate: true,
                "death-date": true,
                "address-postcode": true,
                organisation: true,
            };

            // If provided, validate birthdate, death-date params
            // TODO: birthdate range
            ["birthdate", "death-date"].forEach(dateParam => {
                if (request.query[dateParam] && dateValidator.dateSchema.validate(request.query[dateParam]).error) {
                    throw Boom.badRequest(
                        `${dateParam} has invalid format: ${request.query[dateParam]} is not in YYYY-MM-DD format`,
                        {operationOutcomeCode: "value", apiErrorCode: "invalidDateFormat"})
                }

            });

            // Check for too few search params
            // TODO: Improve this - currently checks for *any* search param
            let hasAnySearchParam = false
            for (let p of Object.keys(searchMap)) {
                if (request.query[p]) {
                    hasAnySearchParam = true
                    break
                }
            }
            if (!hasAnySearchParam) {
                throw Boom.badRequest(
                    "Not enough search parameters were provided to be able to make a search",
                    {operationOutcomeCode: "required", apiErrorCode: "tooFewSearchParams"})
            }

            // Build our empty search response
            let response = {
                resourceType: "Bundle",
                type: "searchset",
                timestamp: Date.now(),
                total: 0,
                entry: []
            }

            // Build a response with one patient
            let examplePatientResponse = function() {
                response.total = 1
                response.entry.push({
                    search: {
                        score: 1.0
                    },
                    resource: EXAMPLE_PATIENT_SMITH,
                })
                return response
            }

            // Build example response with 2 patients
            let exampleResponseWithTwoPatients = function () {
                response.total = 2
                response.entry.push({
                    search: {
                        score: 0.8343
                    },
                        resource: [EXAMPLE_PATIENT_SMITH, EXAMPLE_PATIENT_SMYTHE]
                })
                return response
            }

            // Can be moved elsewhere
            let containsSearchParameters = function(searchParameters) {
                for (let p of Object.keys(searchParameters)) {
                    if (!request.query[p] || request.query[p].toLowerCase() !== searchParameters[p].toLowerCase()) {
                        return false
                    }
                }
                return true
            }


            // Check if wildcard provided
            const  wildcardSearchParams = {
                family: "Sm*",
                gender: "female",
                birthdate: "2010-10-22"
            }
            let wildcardMatch = containsSearchParameters(wildcardSearchParams)

            // Perform a search with max result set using the wildcard params and the max-result parameter
            if (wildcardMatch && request.query["_max-results"]) {
                if (isNaN(request.query["_max-results"]) || request.query["_max-results"] < 1) {
                    // Happy path only (For now)
                    throw Boom.badRequest("TBC", {
                        operationOutcomeCode: "TBC", apiErrorCode: "TBC"
                    })
                } else if (request.query["_max-results"] == 1) {
                    return examplePatientResponse()
                } else {
                    return exampleResponseWithTwoPatients()
                }
            // Perform a advanced search as wildcard provided and max-result parameter not set
            } else if (wildcardMatch) {
                return exampleResponseWithTwoPatients()
            }


            // Perform a 'simple search'
            const simpleSearchParams = {
                family: "Smith",
                gender: "female",
                birthdate: "2010-10-22",
            }
            let simpleMatch = containsSearchParameters(simpleSearchParams)
            // If so, try it
            if (simpleMatch) {
                return examplePatientResponse()
            }

            return response
        }
    }
]
