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

    verifyAddressIdNotPresentWhenRequired: function(request) {
        var idRequired = false
        var idPresent = false
        for (let i of Object.keys(request.payload.patches)) {
            let path = request.payload.patches[i].path
            if (path.includes("/address/" && "/line/") || path.includes("/address/" && "/postalCode") || path.includes("/address/" && "/extension")) {
                idRequired = true
            } else if (path.includes("/address/" && "/id")) {
                idPresent = true
            }
        }
        if (idRequired && !idPresent) {
            return true 
        }
    }
}
