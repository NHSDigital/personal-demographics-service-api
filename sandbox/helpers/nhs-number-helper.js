const Boom = require('boom')
const patients = require('../services/patients')
const nhsNumberValidator = require('../validators/nhs-number-validator')

module.exports = {
    /**
     * Used by Patient/{nhsNumber} paths to check it has been supplied in
     * correct format, and is the NHS Number of our example Patient record
     *
     * Returns nothing.
     *
     * Throws an appropriate Boom error message if either of these are wrong
     *
     * @param {*} request - hapi's request object
     */
    checkNhsNumber: function (request) {
        // Validate NHS number is valid format
        // Ideally should be done using options.validate object (https://hapi.dev/tutorials/validation/)
        // But don't know how to customise the returned JSON when done this way
        const validationResult = nhsNumberValidator.nhsNumberSchema.validate(request.params.nhsNumber)
        if (validationResult.error) {
            throw Boom.badRequest(
                `NHS Number ${request.params.nhsNumber} is not a valid NHS number`,
                {operationOutcomeCode: "value", apiErrorCode: "invalidNHSNumber"})
        }

        // Validate NHS number is for our test patient
        if (request.params.nhsNumber != patients.examplePatientSmith.id) {
            throw Boom.notFound(
                `Patient with NHS number ${request.params.nhsNumber} could not be found`,
                {operationOutcomeCode: "not_found", apiErrorCode: "patientNotFound"}
            )
        }
    }
}