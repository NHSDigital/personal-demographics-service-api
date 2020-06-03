
const datefns = require('date-fns')

module.exports = {
    /**
     * Helper method to prepare a response for a FHIR resource JSON object
     *
     * @param {*} h hapi response toolkit
     * @param {*} resource FHIR resource object
     * @param {*} versionId Version Id of the resource
     * @returns hapi response
     */
    createFhirResponse: function(h, resource, versionId) {
        return h.response(resource)
            .etag(versionId, { weak: true })
    },

    /**
     * Helper method to prepare a response for a polling 202 Accepted response
     *
     * @param {*} h hapi response toolkit
     * @param {*} messageId messageId to set as part of the content-location
     * @returns hapi response
     */
    createAcceptedResponse: function(h, messageId) {
        const response = h.response(null);
        response.header('content-location', "/Polling/" + messageId);
        response.header('retry-after', 100);
        response.code(202)
        return response;
    },

    createMessageId: function() {
        return datefns.format(Date.now(), "yyyyMMddHHmmssSSS")
    }
}
