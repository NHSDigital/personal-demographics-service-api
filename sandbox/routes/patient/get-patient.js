const fs = require('fs')
const Boom = require('boom')
const fhirHelper = require('../../helpers/fhir-helper')
const nhsNumberHelper = require('../../helpers/nhs-number-helper')
const dateValidator = require('../../validators/date-validator')

const EXAMPLE_PATIENT = JSON.parse(fs.readFileSync('mocks/Patient-Jane-Smith.json'))

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
            return fhirHelper.createFhirResponse(h, EXAMPLE_PATIENT)
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

            // Perform a 'simple search'
            const simpleSearchParams = {
                family: "Smith",
                given: "Jane",
                gender: "female",
                birthdate: "2010-10-22",
            }
            let simpleMatch = true
            for (let p of Object.keys(simpleSearchParams)) {
                if (!request.query[p] || request.query[p].toLowerCase() !== simpleSearchParams[p].toLowerCase()) {
                    simpleMatch = false
                    break
                }
            }
            // If so, try it
            if (simpleMatch) {
                response.total = 1
                response.entry.push({
                    search: {
                        score: 1.0
                    },
                    resource: EXAMPLE_PATIENT,
                })
            }

            return response
        }
    }
]
