module.exports = {
    /**
     * Helper method to prepare a response for a FHIR resource JSON object
     *
     * @param {*} h hapi response toolkit
     * @param {*} resource FHIR resource object having meta.versionId property
     * @returns hapi response
     */
    createFhirResponse: function(h, resource) {
        return h.response(resource)
            .etag(resource.meta.versionId, { weak: true })
    }
}
