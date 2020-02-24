const Boom = require('boom')
const fs = require('fs')
const lodash = require('lodash')

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

        // Create new object that doesnt contain _max-result parameters as it value can change and is handled later
        function removeMaxResultParameter(parameters) {
            return lodash.pickBy(parameters, (value, key) => key !== "_max-results")
        }

        let searchParamsWithoutMaxResult = removeMaxResultParameter(searchParameters)
        let queryParamsWithoutMaxResult = removeMaxResultParameter(_request.query)

        // Verifies that search parameters match query parameters
        if (!lodash.isEqual(searchParamsWithoutMaxResult, queryParamsWithoutMaxResult)) {
            return false
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

    // Perform daterange search
    const dateRangeSearchParams = {
        family: "Smith",
        gender: "female",
        birthdate: ["ge2010-10-21", "le2010-10-23"]
    }
    let dateRangeMatch = containsSearchParameters(dateRangeSearchParams)
    if (dateRangeMatch) {
        return buildPatientResponse([EXAMPLE_PATIENT_SMITH])
    }
    
    // Perform a fuzzy search 
    const fuzzySearchParams = {
        family: "Smith",
        gender: "female",
        birthdate: "eq2010-10-22",
        given: "Jane",
        "_fuzzy-match": "true"
    }
    let fuzzyMatch = containsSearchParameters(fuzzySearchParams)
    if (fuzzyMatch) {
        return buildPatientResponse([EXAMPLE_PATIENT_SMYTHE], 0.8976)
    } 

    const wildcardSearchParams = {
        family: "Sm*",
        gender: "female",
        birthdate: "eq2010-10-22"
    }
    let wildcardMatch = containsSearchParameters(wildcardSearchParams)
    // Perform a search with max result set using the wildcard params and the max-result parameter
    if (wildcardMatch && _request.query["_max-results"]) {
        if (isNaN(_request.query["_max-results"]) || _request.query["_max-results"] < 1 || _request.query["_max-results"] > 50) {
            // Invalid parameter (Not integer)
            throw Boom.badRequest("TBC", {
                operationOutcomeCode: "TBC", apiErrorCode: "TBC"
            })
        } else if (_request.query["_max-results"] < 2) {
            // max-result smaller than number of results
            throw Boom.badRequest("TBC", {
                operationOutcomeCode: "TBC", apiErrorCode: "TOO_MANY_RESULTS"
            })
        } else {
            // Return Max Result response
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
        birthdate: "eq2010-10-22",
    }
    let simpleMatch = containsSearchParameters(simpleSearchParams)
    // If so, try it
    if (simpleMatch) {
        return buildPatientResponse([EXAMPLE_PATIENT_SMITH])
    }

    return buildPatientResponse()
    
}
    