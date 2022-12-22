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
            * No x-request-id header: 412
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
                    {operationOutcomeCode: "structure", apiErrorCode: "PRECONDITION_FAILED", display: "Required condition was not fulfilled"}
                )
            }

            // Check If-Match header is correct version
            if (!requestValidator.validateIfMatchHeaderIsCorrectVersion(request, patientToUpdate)) {
                throw Boom.preconditionFailed(
                    "Invalid update with error - This resource has changed since you last read. Please re-read and try again with the new version number.",
                    {operationOutcomeCode: "structure", apiErrorCode: "PRECONDITION_FAILED", display: "Required condition was not fulfilled"})
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
                    {operationOutcomeCode: "structure", apiErrorCode: "INVALID_UPDATE", display: "Update is invalid"})
            }

            // check X-Request-ID exists
            if(!("x-request-id" in request.headers)){
                throw Boom.preconditionFailed(
                    "Invalid request with error - X-Request-ID header must be supplied to access this resource",
                    {operationOutcomeCode: "structure", apiErrorCode: "PRECONDITION_FAILED", display: "Required condition was not fulfilled"})
            }

            // Verify that patch replaces the address with all line entries
            requestValidator.validatePatchReplaceAddressAllLineEntries(request, patientToUpdate))

            // Deep Copy the patient
            let patchedPatient = JSON.parse(JSON.stringify(patientToUpdate));

            // Ensure that missing array keys are added first before applying, otherwise patch will fail.
            for (let i of Object.keys(request.payload.patches)) {
                let path = request.payload.patches[i].path
                if (!path.includes("/-")) {
                    continue;
                }
                path = path.replace("/-", "");
                var dataArray = jsonpatch.getValueByPointer(patientToUpdate, path);
                if (!dataArray) {
                    patchedPatient = jsonpatch.applyOperation(patchedPatient,
                        { "op": "add", "path": path, "value": [] },
                        true,
                        false
                    ).newDocument;
                }
            }

            // Apply the submitted patches
            try {
                patchedPatient = jsonpatch.applyPatch(
                    patchedPatient,
                    request.payload.patches,
                    true,
                    false
                ).newDocument
            }
            catch (e) {
                const patchingError = e.message.slice(0, e.message.indexOf('\n')) // Just the first line; rest is tons of extraneous detail
                throw Boom.badRequest(
                    `Invalid patch: ${patchingError}`,
                    {operationOutcomeCode: "structure", apiErrorCode: "INVALID_UPDATE", display: "Update is invalid"})
            }
            patchedPatient.meta.versionId++;

            const messageId = fhirHelper.createMessageId();
            h.context.messages[messageId] = patchedPatient;
            return fhirHelper.createFhirResponse(h, patchedPatient, patchedPatient.meta.versionId)
        }
    }
]
