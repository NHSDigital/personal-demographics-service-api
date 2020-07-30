const Boom = require('boom')
const patients = require('../services/patients')
const nhsNumberValidator = require('../validators/nhs-number-validator')

function _getPatient(nhsNumber) {
    // Ideally should be done using options.validate object (https://hapi.dev/tutorials/validation/)
    // but the returned JSON cannot be customised
    if (!nhsNumber) {
        throw Boom.badRequest(
            `Unsupported Service`,
            {operationOutcomeCode: "processing", apiErrorCode: "UNSUPPORTED_SERVICE"})
    }

    // Validate NHS number is valid format
    if (nhsNumberValidator.nhsNumberSchema.validate(nhsNumber).error) {
        throw Boom.badRequest(
            `Resource Id is invalid`,
            {operationOutcomeCode: "value", apiErrorCode: "INVALID_RESOURCE_ID"})
    }

    // Validate NHS number is for our test patient
    let patient = null;
    Object.keys(patients.retrieve).forEach(key => {
        if (nhsNumber === patients.retrieve[key].id) {
            patient = patients.retrieve[key];
        }
    })

    if (patient == null) {
        throw Boom.notFound(
            `Resource not found`,
            {operationOutcomeCode: "not_found", apiErrorCode: "RESOURCE_NOT_FOUND"}
        )
    }

    return patient;
}

module.exports = {
    /**
     * Used by Patient/{nhsNumber} paths to get our example Patient record
     *
     * Returns the found patient.
     *
     * Throws an appropriate Boom error message if either of these are wrong
     *
     * @param {*} nhsNumber - the nhsNumber to check
     */
    getNhsNumber: function (nhsNumber) {
        return _getPatient(nhsNumber)
    }
}