const Boom = require('boom')
const fhirHelper = require('../../helpers/fhir-helper')

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

            // force 422 unprocessable entity to occur if header is provided
            if("x-force-failure" in request.headers){
                throw Boom.badData(
                    "An internal polling message ID was found however the processing of the request failed" +
                    " in an unexpected way or was cancelled, so the update failed. Please raise these occurrences with our team (via https://digital.nhs.uk/developer/help-and-support)" +
                    " so we can investigate the issue. When raising, quote the message ID.",
                    {
                        operationOutcomeCode: "processing",
                        apiErrorCode: "POLLING_MESSAGE_FAILURE",
                        display: "The polling id was found however the processing of the request failed in an unexpected way or was cancelled"
                    })
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
