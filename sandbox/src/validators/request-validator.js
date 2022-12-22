const { isUUID } = require("validator");

module.exports = {
    
    validateIfMatchParameter: function (request) {
        return request.headers["if-match"] && (request.headers["if-match"].startsWith('W/"') && request.headers["if-match"].endsWith('"'))
    },

    validateIfMatchHeaderIsCorrectVersion: function(request, examplePatient) {
        return request.headers["if-match"].slice(3, -1) == examplePatient.meta.versionId
    },

    validateContentTypeHeader: function (request) {
        // Allowing application/json-patch+json and application/json because of an issue with apigee and application/json-patch+json
        return request.headers["content-type"] && (
            request.headers["content-type"].toLowerCase() === "application/json-patch+json" ||
            request.headers["content-type"].toLowerCase() === "application/json"
        )
    },

    verifyPatchObjectHasBeenSubmitted: function(request) {
        return request.payload && request.payload.patches && request.payload.patches.length !== 0
    },

    validateRequestIdHeader: ({ headers: { "x-request-id": xRequestId }}) => !!xRequestId && isUUID(xRequestId, 4),

    validatePatchReplaceAddressAllLineEntries: function(request, patientToUpdate) {
        if (patientToUpdate.meta.security[0].display == "restricted") return

        for (let i of Object.keys(request.payload.patches)) {
            let path = request.payload.patches[i].path
            let pathValue = path.split("/").pop()
            if (pathValue == "line") {
                return true
            }
        }
        throw Boom.badRequest(
            "Invalid update with error - Invalid patch - can't replace non-existent object 'line'",
            {operationOutcomeCode: "structure", apiErrorCode: "INVALID_UPDATE", display: "Update is invalid"})
    }
}
