const Boom = require('boom')
const patients = require('../../services/patients')
const fhirHelper = require('../../helpers/fhir-helper')
const nhsNumberHelper = require('../../helpers/nhs-number-helper')
const dateValidator = require('../../validators/date-validator')
const patientSearcher = require("../../services/patient-searcher")

module.exports = [
    /* Patient retrieve
        Behaviour Implemented:
         * Provide ?9000000009: 200 + recieve example patient record as search result
    */
    {
        method: 'GET',
        path: '/Patient/{nhsNumber}',
        handler: (request, h) => {
            nhsNumberHelper.checkNhsNumber(request)
            return fhirHelper.createFhirResponse(h, patients.examplePatientSmith)
        }
    },

    /* Patient search
        Behaviour implemented:
         * Provide no recognised search params: 400 + Appropriate error
         * Provide improperly-specified birthdate/death-date param: 400 + Appropriate error
         * Provide *some* search params: 200 + Empty search response
         * Provide ?birthdate=eq2010-10-22&family=Smith&given=Jane&gender=female: 200 + receive example patient as search result
         * Provide ?birthdate=eq2010-10-22&family=Sm*&gender=female: 200 + receive search result of two example patients
         * Provide ?birthdate=eq2010-10-22&family=Sm*&gender=female&_max-results=2: 200 + receive search result of two example patients
         * Provide ?birthdate=le2010-10-23&birthdate=ge2010-10-21&family=Smith&gender=female: 200 + receive example patient as search result
    */
    {
        method: 'GET',
        path: '/Patient',
        handler: (request) => {

            if (!patientSearcher.requestContainsParameters(request)) {
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

            return patientSearcher.search(request)
        }
    }
]
