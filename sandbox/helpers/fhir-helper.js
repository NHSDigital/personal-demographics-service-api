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
    }
}
