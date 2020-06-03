const Boom = require('boom')
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
            const nhsNumber = request.params.nhsNumber;
            const patientToUpdate = nhsNumberHelper.getNhsNumber(nhsNumber);

            // Check If-Match header exists
            if (!requestValidator.validateIfMatchParameter(request)) {
                throw Boom.preconditionFailed(
                    "Invalid update with error - If-Match header must be supplied to update this resource",
                    {operationOutcomeCode: "structure", apiErrorCode: "PRECONDITION_FAILED"}
                )
            }

            // Check If-Match header is correct version
            if (!requestValidator.validateIfMatchHeaderIsCorrectVersion(request, patientToUpdate)) {
                throw Boom.preconditionFailed(
                    "Invalid update with error - This resource has changed since you last read. Please re-read and try again with the new version number.",
                    {operationOutcomeCode: "structure", apiErrorCode: "PRECONDITION_FAILED"})
            }

            // Check Content-Type header
            if (!requestValidator.validateContentTypeHeader(request)) {
                throw Boom.badRequest(
                    "Unsupported Service",
                    {operationOutcomeCode: "processing", apiErrorCode: "UNSUPPORTED_SERVICE"})
            }

            // Verify at least one patch object has been submitted
            if (!requestValidator.verifyPatchObjectHasBeenSubmitted(request)) {
                throw Boom.badRequest(
                    "Invalid update with error - No patches found",
                    {operationOutcomeCode: "structure", apiErrorCode: "INVALID_UPDATE"})
            }

            // Apply the submitted patches
            let patchedPatient
            try {
                patchedPatient = jsonpatch.applyPatch(
                    patientToUpdate,
                    request.payload.patches,
                    true,
                    false
                ).newDocument
            }
            catch (e) {
                const patchingError = e.message.slice(0, e.message.indexOf('\n')) // Just the first line; rest is tons of extraneous detail
                throw Boom.badRequest(
                    `Invalid patch: ${patchingError}`,
                    {operationOutcomeCode: "structure", apiErrorCode: "INVALID_UPDATE"})
            }
            patchedPatient.meta.versionId++;

            const messageId = fhirHelper.createMessageId();
            h.context.messages[messageId] = patchedPatient;
            return fhirHelper.createAcceptedResponse(h, messageId);
        }
    }
]
