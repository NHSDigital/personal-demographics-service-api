const Boom = require('boom')
const fhirHelper = require('../../helpers/fhir-helper')
const nhsNumberHelper = require('../../helpers/nhs-number-helper')
const relatedPersonHelper = require('../../helpers/related-person-helper')
const dateValidator = require('../../validators/date-validator')
const patientSearcher = require("../../services/patient-searcher")

module.exports = [
    /* Patient retrieve
        Behaviour Implemented:
        * Provide ?9000000009: 200 + recieve example patient record as search result
        * No x-request-id header: 400
    */
    {
        method: 'GET',
        path: '/Patient/{parameters*}',
        handler: (request, h) => {
            // HAPI Server does not seem to support multiple ids in paths - such as:
            //   /Patient/9000000009/RelatedPerson
            // so need to force it like this.
            const params = request.params.parameters.split("/");
            const nhsNumber = params[0];
            const resource = params.length > 1 ? params[1] : null;
            const objectId = params.length > 2 ? params[2] : null;

            const patient = nhsNumberHelper.getNhsNumber(nhsNumber);

            // check X-Request-ID exists
            if(!("x-request-id" in request.headers)){
                throw Boom.badRequest(
                    "Invalid request with error - X-Request-ID header must be supplied to access this resource",
                    {operationOutcomeCode: "required", apiErrorCode: "MISSING_VALUE", display: "Required value is missing"})
            }

            if (resource == null) {
                // For example /Patient/9000000009
                return fhirHelper.createFhirResponse(h, patient, patient.meta.versionId);

            } else if (resource && objectId == null) {
                // For example /Patient/9000000009/RelatedPerson
                const response = relatedPersonHelper.getRelatedPersons(nhsNumber);
                return fhirHelper.createFhirResponse(h, response, patient.meta.versionId);
            }
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
         * No x-request-id header: 400
    */
    {
        method: 'GET',
        path: '/Patient',
        handler: (request) => {

            // check X-Request-ID exists
            if(!("x-request-id" in request.headers)){
                throw Boom.badRequest(
                    "Invalid request with error - X-Request-ID header must be supplied to access this resource",
                    {operationOutcomeCode: "required", apiErrorCode: "MISSING_VALUE", display: "Required value is missing"})
            }

            function dateFormat(date) {
                if (date.match(/^\d/)) {
                    // Allow 2020-03-27 and eq2020-03-27 - adding on the 'eq' if missing as the (imported) validator expects it.
                    date = "eq" + date;
                }
                return date
            }

            if (!patientSearcher.requestContainsParameters(request)) {
                throw Boom.badRequest(
                    "Not enough search parameters were provided for a valid search, you must supply family and birthdate as a minimum and only use recognised parameters from the api catalogue.",
                    {operationOutcomeCode: "required", apiErrorCode: "MISSING_VALUE", display: "Required value is missing"})
            }

            if (request.query["birthdate"]) {
                let birthdateParameter = Array.isArray(request.query["birthdate"]) ? request.query["birthdate"] : [request.query["birthdate"]]
                birthdateParameter.forEach(date => {  
                    date = dateFormat(date)
                    if (dateValidator.dateSchema.validate(date).error) { 
                        throw Boom.badRequest(
                            `Invalid value - '${request.query["birthdate"]}' in field 'birthdate'`,
                            {operationOutcomeCode: "value", apiErrorCode: "INVALID_SEARCH_DATA", display: "Search data is invalid"})
                    }
                }) 
            }

            if (request.query["death-date"]) {
                var date = request.query["death-date"]
                date = dateFormat(date)
                if(dateValidator.dateSchema.validate(date).error) {
                    throw Boom.badRequest(
                        `Invalid value - '${request.query["death-date"]}' in field 'death-date'`,
                        {operationOutcomeCode: "value", apiErrorCode: "INVALID_SEARCH_DATA", display: "Search data is invalid"})
                }
            }

            return patientSearcher.search(request)
        }
    }
]
