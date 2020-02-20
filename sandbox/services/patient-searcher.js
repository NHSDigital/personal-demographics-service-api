const Boom = require('boom')
const fs = require('fs')

const EXAMPLE_PATIENT_SMITH = JSON.parse(fs.readFileSync('mocks/Patient-Jane-Smith.json'))
const EXAMPLE_PATIENT_SMYTHE = JSON.parse(fs.readFileSync('mocks/Patient-Jayne-Smyth.json'))

let _request;

module.exports.init = function(request) {
    _request = request;
    return exports
}

// Verify search contains parameters
module.exports.requestContainsParameters = function() {
    const searchMap = {
        "_exact-match": true,
        "_history": true,
        "_fuzzy-match": true,
        "_max-results": true,
        family: '$.name[?(@.use="usual")].family', // Usual family name
        given: true,
        gender: true,
        birthdate: true,
        "death-date": true,
        "address-postcode": true,
        organisation: true,
    };

    let hasAnySearchParam = false
    for (let p of Object.keys(searchMap)) {
        if (_request.query[p]) {
            hasAnySearchParam = true
            break
        }
    }
    return hasAnySearchParam
}

// Determine which 'search' to perform based on parameters passed
module.exports.search = function() {

    function containsSearchParameters(searchParameters) {
        for (let p of Object.keys(searchParameters)) {
            if (!_request.query[p] || _request.query[p].toLowerCase() !== searchParameters[p].toLowerCase()) {
                return false
            }
        }
        return true
    }
    
    function buildPatientResponse(examplePatients = [], searchScore = 1.0) {
        let response = {
            resourceType: "Bundle",
            type: "searchset",
            timestamp: Date.now(),
            total: examplePatients.length,
            entry: []
        }
        if (examplePatients.length > 0) {
            response.entry.push({
                search: {
                    score: searchScore
                },
                resource: examplePatients,
            })
        }
        return response
    }

    // const dateRangeSearchParams = {
    //     //TBC
    // }
    
    // Perform a fuzzy search 
    const fuzzySearchParams = {
        family: "Smith",
        gender: "female",
        birthdate: "2010-10-22",
        given: "Jane",
        "_fuzzy-match": "true"
    }
    let fuzzyMatch = containsSearchParameters(fuzzySearchParams)
    if (fuzzyMatch) {
        return buildPatientResponse([EXAMPLE_PATIENT_SMYTHE])
    } 

    const wildcardSearchParams = {
        family: "Sm*",
        gender: "female",
        birthdate: "2010-10-22"
    }
    let wildcardMatch = containsSearchParameters(wildcardSearchParams)
    // Perform a search with max result set using the wildcard params and the max-result parameter
    if (wildcardMatch && _request.query["_max-results"]) {
        if (isNaN(_request.query["_max-results"]) || _request.query["_max-results"] < 1 || _request.query["_max-results"] > 50) {
            // not integer
            throw Boom.badRequest("TBC", {
                operationOutcomeCode: "TBC", apiErrorCode: "TBC"
            })
        } else if (_request.query["_max-results"] < 2) {
            // max-result smaller than number of results
            throw Boom.badRequest("TBC", {
                operationOutcomeCode: "TBC", apiErrorCode: "TOO_MANY_RESULTS"
            })
        } else {
            return buildPatientResponse([EXAMPLE_PATIENT_SMITH, EXAMPLE_PATIENT_SMYTHE], 0.8343)
        } 
    // Perform a advanced search as wildcard provided and max-result parameter not set
    } else if (wildcardMatch) {
        return buildPatientResponse([EXAMPLE_PATIENT_SMITH, EXAMPLE_PATIENT_SMYTHE], 0.8343)
    }

    // Perform a 'simple search'
    const simpleSearchParams = {
        family: "Smith",
        gender: "female",
        birthdate: "2010-10-22",
    }
    let simpleMatch = containsSearchParameters(simpleSearchParams)
    // If so, try it
    if (simpleMatch) {
        return buildPatientResponse([EXAMPLE_PATIENT_SMITH])
    }

    return buildPatientResponse()
    
}
    