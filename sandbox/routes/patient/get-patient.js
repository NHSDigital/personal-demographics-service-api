const fs = require('fs')
const Boom = require('boom')
const fhirHelper = require('../../helpers/fhir-helper')
const nhsNumberHelper = require('../../helpers/nhs-number-helper')
const dateValidator = require('../../validators/date-validator')

const EXAMPLE_PATIENT_SMITH = JSON.parse(fs.readFileSync('mocks/Patient.json'))

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

            if (request.query["birthdate"]) {
                let birthdateParameter = Array.isArray(request.query["birthdate"]) ? request.query["birthdate"] : [request.query["birthdate"]]
                birthdateParameter.forEach(date => {   
                    if (dateValidator.birthdateSchema.validate(date).error) { 
                        throw Boom.badRequest(
                            // Decide on format string instead of [a-z]YYYY-MM-DD
                            `birthdate has invalid format: ${request.query["birthdate"]} is not in [a-z]YYYY-MM-DD format`,
                            {operationOutcomeCode: "value", apiErrorCode: "invalidDateFormat"})
                    }
                }) 
            }

            if (request.query["death-date"] && dateValidator.dateSchema.validate(request.query["death-date"]).error) {
                throw Boom.badRequest(
                    `death-date has invalid format: ${request.query["death-date"]} is not in YYYY-MM-DD format`,
                    {operationOutcomeCode: "value", apiErrorCode: "invalidDateFormat"})
            }

            return patientSearcher.search()
        }
    }
]
