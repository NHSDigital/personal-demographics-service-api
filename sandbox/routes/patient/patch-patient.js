const Boom = require('boom')
const patients = require('../../services/patients')
const nhsNumberHelper = require('../../helpers/nhs-number-helper')
const fhirHelper = require('../../helpers/fhir-helper')
const jsonpatch = require('fast-json-patch')
const requestValidator = require("../../validators/request-validator")

module.exports = [
    {
        /*
            Patient partial update
            Behaviour:
            * No If-Match Header: 400
            * If-Match header does not match resource latest: 412 Precondition Failed
            * Invalid request body: 400(?)
            * Non-existant patient: 404 
            * Invalid NHS Number: 400 
            * Unset/invalid Content-Type: 415 Unsupported Media Type
        */
        method: 'PATCH',
        path: '/Patient/{nhsNumber}',
        handler: (request, h) => {
            nhsNumberHelper.checkNhsNumber(request)

            // Check If-Match header exists
            if (!requestValidator.validateIfMatchParameter(request)) {
                throw Boom.badRequest(
                    "If-Match header must be supplied to update this resource",
                    {operationOutcomeCode: "required", apiErrorCode: "MISSING_IF_MATCH_HEADER"}
                )
            }

            // Check If-Match header is correct version
            if (!requestValidator.validateIfMatchHeaderIsCorrectVersion(request, patients.examplePatientSmith)) {
                throw Boom.preconditionFailed(
                    "This resource has changed since you last read. Please re-read and try again with the new version number.",
                    {operationOutcomeCode: "conflict", apiErrorCode: "INVALID_IF_MATCH_HEADER"})
            }

            // Check Content-Type header
            if (!requestValidator.validateContentTypeHeader(request)) {
                // TODO: What's the proper error here?
                throw Boom.unsupportedMediaType(
                    "Must be application/json-patch+json",
                    {operationOutcomeCode: "value", apiErrorCode: "unsupportedMediaType"})
            }

            // Verify at least one patch object has been submitted
            if (!requestValidator.verifyPatchObjectHasBeenSubmitted(request)) {
                // TODO: Proper error message
                throw Boom.badRequest(
                    "No patches submitted",
                    {operationOutcomeCode: "required", apiErrorCode: "noPatchesSubmitted"})
            }

            // Apply the submitted patches
            let patchedPatient
            try {
                patchedPatient = jsonpatch.applyPatch(patients.examplePatientSmith, request.payload.patches, true, false).newDocument
            }
            catch (e) {
                const patchingError = e.message.slice(0, e.message.indexOf('\n')) // Just the first line; rest is tons of extraneous detail
                throw Boom.badRequest(
                    `Invalid patch: ${patchingError}`,
                    {operationOutcomeCode: "value", apiErrorCode: "invalidPatchOperation"})
            }
            patchedPatient.meta.versionId++

            return fhirHelper.createFhirResponse(h, patchedPatient)
        }
    }
]
