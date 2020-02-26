
let _request;

module.exports.init = function(request) {
    _request = request;
    return exports
}

module.exports = {
    
    validateIfMatchParameter: function () {
        return _request.headers["if-match"] || (_request.headers["if-match"].startsWith('W/"') && _request.headers["if-match"].endsWith('"'))
    },

    validateIfMatchHeaderIsCorrectVersion: function(examplePatient) {
        return _request.headers["if-match"].slice(3, -1) == examplePatient.meta.versionId
    },

    validateContentTypeHeader: function () {
        return _request.headers["content-type"] || _request.headers["content-type"].toLowerCase() === "application/json-patch+json"
    },

    verifyPatchObjectHasBeenSubmitted: function() {
        return _request.payload || _request.payload.patches || _request.payload.patches.length !== 0
    }
}