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
                fullUrl: "https://api.service.nhs.uk/personal-demographics/FHIR/R4/Patient/" + patient["id"],
                search: {
                    score: searchScore
                },
                resource: patient,
            })
        });

    } else {
        delete response.entry;
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

    // let validParams = [request.query.family,request.query.birthedate,request.query.given,request.query.gender,request.query.death-date,
    //                     request.query.address-postcode,request.query.general-practitioner,request.query.phone,request.query.email]

    // let notEnoughValidParamsCounter = 0;
    // for (let param in validParams) {
    //     console.log(param);
    //     if (!param) {
    //     notEnoughValidParamsCounter++;
    //     }
    // }
    // if (notEnoughValidParamsCounter === validParams.length) {
    //     throw Boom.notImplemented(`This mock endpoint has no example response for this combination of search parameters`,
    //     {operationOutcomeCode: "not-supported", apiErrorCode: "not-supported", display: "Unsupported operation"})
    // }

    // Check for default 'Try this API' params
    const tryThisApiParams = {
        "_fuzzy-match": "false",
        "_exact-match": "false",
        "_history": "true",
        "_max-results": 1,
        family: "Smith",
        given: "Jane",
        gender: "female",
        birthdate: "eq2010-10-22",
        "death-date": "eq2010-10-22",
        "address-postcode": "LS1 6AE",
        "general-practitioner": "Y12345"
    }

    // Check for default 'Try this Api' params inc. phone
    const tryPhoneApiParams = {
        "_fuzzy-match": "false",
        "_exact-match": "false",
        "_history": "true",
        "_max-results": 1,
        family: "Smith",
        given: "Jane",
        gender: "female",
        birthdate: "eq2010-10-22",
        "death-date": "eq2010-10-22",
        "address-postcode": "LS1 6AE",
        "general-practitioner": "Y12345",
        "phone": "01632960587"
    }

    // Check for default 'Try this Api' params inc. email
    const tryEmailApiParams = {
        "_fuzzy-match": "false",
        "_exact-match": "false",
        "_history": "true",
        "_max-results": 1,
        family: "Smith",
        given: "Jane",
        gender: "female",
        birthdate: "eq2010-10-22",
        "death-date": "eq2010-10-22",
        "address-postcode": "LS1 6AE",
        "general-practitioner": "Y12345",
        "email": "jane.smith@example.com"
    }

    // Check for default 'Try this Api' params inc. email and phone
    const tryEmailPhoneApiParams = {
        "_fuzzy-match": "false",
        "_exact-match": "false",
        "_history": "true",
        "_max-results": 1,
        family: "Smith",
        given: "Jane",
        gender: "female",
        birthdate: "eq2010-10-22",
        "death-date": "eq2010-10-22",
        "address-postcode": "LS1 6AE",
        "general-practitioner": "Y12345",
        "phone": "01632960587",
        "email": "jane.smith@example.com"
    }

    // daterange search params
    const dateRangeSearchParams = {
        family: "Smith",
        gender: "female",
        birthdate: ["ge2010-10-21", "le2010-10-23"]
    }

    // fuzzy search params
    const fuzzySearchParams = {
        family: "Smith",
        gender: "female",
        birthdate: "eq2010-10-22",
        given: "Jane",
        "_fuzzy-match": "true"
    }

    // wildcard search params
    const wildcardDefaultSearchParams = {
        family: "Sm*",
        gender: "female",
        birthdate: "eq2010-10-22"
    }

    // wildcard search inc phone params
    const wildcardPhoneSearchParams = {
        family: "Sm*",
        gender: "female",
        birthdate: "eq2010-10-22",
        phone: "01632960587"
    }

    // wildcard search inc email params
    const wildcardEmailSearchParams = {
        family: "Sm*",
        gender: "female",
        birthdate: "eq2010-10-22",
        email: "jane.smith@example.com"
    }

    // simple search params
    const simpleSearchParams = {
        family: "Smith",
        gender: "female",
        birthdate: "eq2010-10-22",
    }

    // simple search 'gender' free params
    const simpleSearchParamsGenderFree = {
        family: "Smith",
        birthdate: "eq2010-10-22",
    }

    // simple search params inc phone
    const simplePhoneSearchParams = {
        family: "Smith",
        gender: "female",
        birthdate: "eq2010-10-22",
        phone: "01632960587"
    }

    // simple search 'gender' free params inc phone
    const simplePhoneSearchParamsGenderFree = {
        family: "Smith",
        birthdate: "eq2010-10-22",
        phone: "01632960587"
    }

    // simple search params inc email
    const simpleEmailSearchParams = {
        family: "Smith",
        gender: "female",
        birthdate: "eq2010-10-22",
        email: "jane.smith@example.com"
    }

    // simple search 'gender' free params inc email
    const simpleEmailSearchParamsGenderFree = {
        family: "Smith",
        birthdate: "eq2010-10-22",
        email: "jane.smith@example.com"
    }

    // simple search params inc email and phone
    const simpleEmailPhoneSearchParams = {
        family: "Smith",
        gender: "female",
        birthdate: "eq2010-10-22",
        phone: "01632960587",
        email: "jane.smith@example.com"
    }

    // simple search 'gender' free params inc email and phone
    const simpleEmailPhoneSearchParamsGenderFree = {
        family: "Smith",
        birthdate: "eq2010-10-22",
        phone: "01632960587",
        email: "jane.smith@example.com"
    }

    // 'sensitive search' params
    const sensitiveSearchParams = {
        family: "Smythe",
        given: "Janet",
        gender: "female",
        birthdate: "eq2005-06-16",
    }

    // Multi name search params
    const multiNameSearchParams = {
        family: "Smith",
        given: ["John Paul", "James"],
        gender: "male",
        birthdate: "eq2010-10-22",
        "_fuzzy-match": "false",
        "_exact-match": "false",
        "_history": "true",
        }

    let wildcardMatch = containsSearchParameters(request, wildcardDefaultSearchParams)
    let wildcardPhoneMatch = containsSearchParameters(request, wildcardPhoneSearchParams)
    let wildcardEmailMatch = containsSearchParameters(request, wildcardEmailSearchParams)
    let wildcardTelecomMatch = false;
    if (wildcardEmailMatch) {
        wildcardTelecomMatch = wildcardEmailMatch
    } else if (wildcardPhoneMatch) {
        wildcardTelecomMatch = wildcardPhoneMatch
    }
    // Perform a search with max result set using the wildcard params and the max-result parameter
    if ((wildcardMatch && request.query["_max-results"]) || (wildcardTelecomMatch && request.query["_max-results"])) {
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
    } else if (wildcardTelecomMatch) {
        return buildPatientResponse([patients.search.exampleSearchPatientSmith])
    }
    

    if ((containsSearchParameters(request,tryThisApiParams)) || (containsSearchParameters(request,tryPhoneApiParams)) || (containsSearchParameters(request,tryEmailApiParams)) ||
    (containsSearchParameters(request,tryEmailPhoneApiParams)) || (containsSearchParameters(request,dateRangeSearchParams)) || (containsSearchParameters(request,simpleSearchParams)) ||
    (containsSearchParameters(request,simpleSearchParamsGenderFree)) || (containsSearchParameters(request,simplePhoneSearchParams)) || (containsSearchParameters(request,simplePhoneSearchParamsGenderFree)) ||
    (containsSearchParameters(request,simpleEmailSearchParams)) || (containsSearchParameters(request,simpleEmailSearchParamsGenderFree)) || (containsSearchParameters(request,simpleEmailPhoneSearchParams)) ||
    (containsSearchParameters(request,simpleEmailPhoneSearchParamsGenderFree))) {
        return buildPatientResponse([patients.search.exampleSearchPatientSmith])
    }

    if (containsSearchParameters(request, fuzzySearchParams)) {
        return buildPatientResponse([patients.search.exampleSearchPatientSmyth], 0.8976)
    }

    if (containsSearchParameters(request, sensitiveSearchParams)) {
        return buildPatientResponse([patients.search.exampleSearchPatientSmythe]);
    }

    
    if (containsSearchParameters(request, multiNameSearchParams)) {
        return buildPatientResponse([patients.search.exampleSearchPatientCompoundName])
    }

    return buildPatientResponse([])
}

