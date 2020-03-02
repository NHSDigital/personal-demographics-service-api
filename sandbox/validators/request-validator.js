
module.exports = {
    
    validateIfMatchParameter: function (request) {
        return request.headers["if-match"] || (request.headers["if-match"].startsWith('W/"') && request.headers["if-match"].endsWith('"'))
    },

    validateIfMatchHeaderIsCorrectVersion: function(request, examplePatient) {
        return request.headers["if-match"].slice(3, -1) == examplePatient.meta.versionId
    },

    validateContentTypeHeader: function (request) {
        return request.headers["content-type"] || request.headers["content-type"].toLowerCase() === "application/json-patch+json"
    },

    verifyPatchObjectHasBeenSubmitted: function(request) {
        return request.payload || request.payload.patches || request.payload.patches.length !== 0
    }
}