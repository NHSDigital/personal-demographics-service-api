const fs = require('fs')
const Boom = require('boom')
const fhirHelper = require('../../helpers/fhir-helper')
const nhsNumberHelper = require('../../helpers/nhs-number-helper')
const dateValidator = require('../../validators/date-validator')

const EXAMPLE_PATIENT_SMITH = JSON.parse(fs.readFileSync('mocks/Patient-Jane-Smith.json'))

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
            
            let patientSearcher = require("../../services/patient-searcher").init(request)

            if (!patientSearcher.requestContainsParameters()) {
                throw Boom.badRequest(
                    "Not enough search parameters were provided to be able to make a search",
                    {operationOutcomeCode: "required", apiErrorCode: "tooFewSearchParams"})
            }

            // If provided, validate birthdate, death-date params
            // TODO: birthdate range
            ["birthdate", "death-date"].forEach(dateParam => {
                if (request.query[dateParam] && dateValidator.dateSchema.validate(request.query[dateParam]).error) {
                    throw Boom.badRequest(
                        `${dateParam} has invalid format: ${request.query[dateParam]} is not in YYYY-MM-DD format`,
                        {operationOutcomeCode: "value", apiErrorCode: "invalidDateFormat"})
                }

            });

            return patientSearcher.search()
        }
    }
]
