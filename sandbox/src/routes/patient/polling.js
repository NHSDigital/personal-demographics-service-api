const Boom = require('boom')
const fhirHelper = require('../../helpers/fhir-helper')
const { mockSpinePollingErrors } = require("../../helpers/simulate-spine-errors-helper");

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
        method: 'GET',
        path: '/_poll/{messageId}',
        handler: (request, h) => {
            // force a simulated error if the header is provided
            const { "x-mock-spine-error": mockErrorCode } = request.headers;
            if(mockErrorCode in mockSpinePollingErrors){
                mockSpinePollingErrors[mockErrorCode]();
            }

            const messageId = request.params.messageId
            const patchedPatient = h.context.messages[messageId];


            if (messageId === "20200522091633363041_000001") {
                return fhirHelper.createAcceptedResponse(h, messageId)
            } else {
                if (!patchedPatient) {
                    throw Boom.notFound(
                        "The polling id was not found",
                        {
                            operationOutcomeCode: "non-found",
                            operationOutcomeSeverity: "information",
                            apiErrorCode: "POLLING_ID_NOT_FOUND"
                        }
                    )
                }
                return fhirHelper.createFhirResponse(h, patchedPatient, patchedPatient.meta.versionId)
            }
        }
    }
]
