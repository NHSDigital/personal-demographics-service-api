const Boom = require('boom')
const patients = require('../services/patients')
const nhsNumberValidator = require('../validators/nhs-number-validator')

function _getPatient(nhsNumber) {
    // Ideally should be done using options.validate object (https://hapi.dev/tutorials/validation/)
    // But don't know how to customise the returned JSON when done this way
    if (!nhsNumber) {
        throw Boom.badRequest(
            `Unsupported Service`,
            {operationOutcomeCode: "processing", apiErrorCode: "UNSUPPORTED_SERVICE"})
    }

    // Validate NHS number is valid format
    if (nhsNumberValidator.nhsNumberSchema.validate(nhsNumber).error) {
        throw Boom.badRequest(
            `NHS Number ${nhsNumber} is not a valid NHS number`,
            {operationOutcomeCode: "value", apiErrorCode: "INVALID_NHS_NUMBER"})
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
            `Patient with NHS number ${nhsNumber} could not be found`,
            {operationOutcomeCode: "not_found", apiErrorCode: "PATIENT_NOT_FOUND"}
        )
    }

    return patient;
}

module.exports = {
    /**
     * Used by Patient/{nhsNumber} paths to check it has been supplied in
     * correct format, and is the NHS Number of our example Patient record
     *
     * Returns nothing.
     *
     * Throws an appropriate Boom error message if either of these are wrong
     *
     * @param {*} nhsNumber - the nhsNumber to check
     */
    checkNhsNumber: function (nhsNumber) {
        _getPatient(nhsNumber)
    },


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