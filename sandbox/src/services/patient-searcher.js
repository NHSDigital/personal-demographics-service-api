const Boom = require('boom')
const lodash = require('lodash')
const datefns = require('date-fns')
const patients = require('./patients')

function containsSearchParameters(request, searchParameters) {

    // Create new object that doesnt contain _max-result parameters as it value can change and is handled later
    function removeMaxResultParameter(parameters) {
        return lodash.pickBy(parameters, (value, key) => key !== "_max-results");
    }

    // Lowercases all the paramater values - so that 'smith' will match 'Smith'
    function lowerValues(parameters) {
        return lodash.mapValues(parameters, function(val){
            return lodash.isString(val) ? val.toLowerCase() : val;
        });
    }

    // Remove date 'eq' prefix, as it is optional.
    function dateFormat(parameters) {
        return lodash.mapValues(parameters, function(val, key){
            if ((key == "birthdate" || key == "death-date") && 
                    (lodash.isString(val) && val.startsWith("eq"))) {
                return lodash.isString(val) ? val.replace("eq", "") : val;
            }
            return val;
        });
    }

    var formattedSearchParams = searchParameters;
    var formattedQueryParams = request.query;

    let formattingFuncs = [removeMaxResultParameter, lowerValues, dateFormat];
    formattingFuncs.forEach(func => {
        formattedSearchParams = func(formattedSearchParams);
        formattedQueryParams = func(formattedQueryParams);
    });

    // Verifies that search parameters match query parameters
    if (!lodash.isEqual(formattedSearchParams, formattedQueryParams)) {
        return false;
    }

    return true;
}

function buildPatientResponse(examplePatients = [], searchScore = 1.0) {
    let response = {
        resourceType: "Bundle",
        type: "searchset",
        timestamp: datefns.format(Date.now(), "yyyy-MM-dd'T'HH:mm:ss+00:00"),
        total: examplePatients.length,
        entry: []
    }

    if (examplePatients.length > 0) {
        examplePatients.forEach(patient => {
            response.entry.push({
                fullUrl: "https://beta.api.digital.nhs.uk/personal-demographics/Patient/" + patient["id"],
                search: {
                    score: searchScore
                },
                resource: patient,
            })
        });
    } else {
        delete response.entry
    }   

    return response;
}

// Verify search contains parameters
module.exports.requestContainsParameters = function(request) {
    const searchMap = {
        "_exact-match": true,
        "_history": true,
        "_fuzzy-match": true,
        "_max-results": true,
        family: "$.name[?(@.use='usual')].family", // Usual family name
        given: true,
        gender: true,
        birthdate: true,
        "death-date": true,
        "address-postcode": true,
        organisation: true,
    };

    let hasAnySearchParam = false
    for (let p of Object.keys(searchMap)) {
        if (request.query[p]) {
            hasAnySearchParam = true
            break
        }
    }
    return hasAnySearchParam;
}

// Determine which 'search' to perform based on parameters passed
module.exports.search = function(request) {

    // Perform daterange search
    const dateRangeSearchParams = {
        family: "Smith",
        gender: "female",
        birthdate: ["ge2010-10-21", "le2010-10-23"]
    }
    if (containsSearchParameters(request, dateRangeSearchParams)) {
        return buildPatientResponse([patients.search.exampleSearchPatientSmith])
    }
    
    // Perform a fuzzy search 
    const fuzzySearchParams = {
        family: "Smith",
        gender: "female",
        birthdate: "eq2010-10-22",
        given: "Jane",
        "_fuzzy-match": "true"
    }
    if (containsSearchParameters(request, fuzzySearchParams)) {
        return buildPatientResponse([patients.search.exampleSearchPatientSmyth], 0.8976)
    } 

    // Check for wildcard search
    const wildcardSearchParams = {
        family: "Sm*",
        gender: "female",
        birthdate: "eq2010-10-22"
    }
    let wildcardMatch = containsSearchParameters(request, wildcardSearchParams)
    // Perform a search with max result set using the wildcard params and the max-result parameter
    if (wildcardMatch && request.query["_max-results"]) {
        if (isNaN(request.query["_max-results"]) || request.query["_max-results"] < 1 || request.query["_max-results"] > 50) {
            // Invalid parameter (Not integer)
            throw Boom.badRequest("Invalid value - '" + request.query["_max-results"] + "' in field '_max-results'", {
                operationOutcomeCode: "value", apiErrorCode: "INVALID_VALUE", display: "Provided value is invalid"
            })
        } else if (request.query["_max-results"] < 2) {
            // max-result smaller than number of results
            throw Boom.badRequest("Too Many Matches", {
                operationOutcomeCode: "not-found", 
                operationOutcomeSeverity: "information",
                apiErrorCode: "TOO_MANY_MATCHES"
            })
        } else {
            // Return Max Result response
            return buildPatientResponse([patients.search.exampleSearchPatientSmith, patients.search.exampleSearchPatientSmyth], 0.8343);
        } 
    // Perform a advanced search as wildcard provided and max-result parameter not set
    } else if (wildcardMatch) {
        return buildPatientResponse([patients.search.exampleSearchPatientSmith, patients.search.exampleSearchPatientSmyth], 0.8343);
    }

    // Perform a 'simple search'
    const simpleSearchParams = {
        family: "Smith",
        gender: "female",
        birthdate: "eq2010-10-22",
    }
    // If so, try it
    if (containsSearchParameters(request, simpleSearchParams)) {
        return buildPatientResponse([patients.search.exampleSearchPatientSmith]);
    }

    // Perform a 'sensitive search'
    const sensitiveSearchParams = {
        family: "Smythe",
        given: "Janet",
        gender: "female",
        birthdate: "eq2005-06-16",
    }
    // If so, try it
    if (containsSearchParameters(request, sensitiveSearchParams)) {
        return buildPatientResponse([patients.search.exampleSearchPatientSmythe]);
    }

    return buildPatientResponse();
    
}
    