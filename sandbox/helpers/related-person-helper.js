const Boom = require('boom')
const datefns = require('date-fns')
const relatedpersons = require('../services/relatedpersons')

function _getRelatedPersons(nhsNumber) {
    let response = [];
        Object.keys(relatedpersons).forEach(key => {
            if (nhsNumber === key) {
                Object.keys(relatedpersons[key]).forEach(responseKey => {
                    response.push(relatedpersons[key][responseKey]);
                })
            }
        })

        if (response.length === 0) {
            throw Boom.notFound(
                `Resource not found`,
                {operationOutcomeCode: "not_found", apiErrorCode: "RESOURCE_NOT_FOUND"}
            )
        }

        return response
}

function buildBundleResponse(exampleResources = [], nhsNumber) {
    let response = {
        resourceType: "Bundle",
        type: "searchset",
        timestamp: datefns.format(Date.now(), "yyyy-MM-dd'T'HH:mm:ss+00:00"),
        total: exampleResources.length,
        entry: []
    }

    if (exampleResources.length > 0) {
        exampleResources.forEach(resource => {
            response.entry.push({
                fullUrl: "https://beta.api.digital.nhs.uk/personal-demographics/Patient/" + nhsNumber + "/RelatedPerson/" + resource["id"],
                resource: resource,
            })
        });
    }
    return response;
}

module.exports = {
    /**
     * Used by Patient/{nhsNumber}/RelatedPerson paths to check it there are any
     * Related Person resources attached to the patients nhsNumber.
     *
     * Returns related person list.
     *
     * Throws an appropriate Boom error message if either of these are wrong
     *
     * @param {*} nhsNumber - the nhsNumber to check
     */
    getRelatedPersons: function (nhsNumber) {
        const relatedPerson = _getRelatedPersons(nhsNumber);
        return buildBundleResponse(relatedPerson, nhsNumber)
    },


    /**
     * Used by Patient/{nhsNumber}/RelatedPerson/{objectId} paths to check it there are any
     * Related Person resources attached to the patients nhsNumber with a matching objectId.
     *
     * Returns related person object.
     *
     * Throws an appropriate Boom error message if either of these are wrong
     *
     * @param {*} nhsNumber - the nhsNumber to check
     */
    getRelatedPerson: function (nhsNumber, objectId) {
        const relatedPersons = _getRelatedPersons(nhsNumber);

        let relatedPerson = null;
        relatedPersons.forEach(resource => {
            if (objectId === resource.id) {
                relatedPerson = resource;
            }
        })

        if (relatedPerson == null) {
            throw Boom.notFound(
                `Resource not found`,
                {operationOutcomeCode: "not_found", apiErrorCode: "RESOURCE_NOT_FOUND"}
            )
        }
        return relatedPerson;
    }
}