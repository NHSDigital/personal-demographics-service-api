/*
    Stub search responses
*/
const SEARCH_PATIENT_9000000009 = context.read('classpath:mocks/stubs/search_responses/search_patient_9000000009.json');
const SEARCH_PATIENT_9000000017 = context.read('classpath:mocks/stubs/search_responses/search_patient_9000000017.json');
const RESTRICTED_PATIENT_SEARCH = context.read('classpath:mocks/stubs/search_responses/search_patient_9000000025.json');
const COMPOUND_NAME_SEARCH = context.read('classpath:mocks/stubs/search_responses/compound_name_search.json');

const EMPTY_SEARCHSET = { "resourceType":"Bundle","type":"searchset","total":0}
const SIMPLE_SEARCH = {
    "resourceType": "Bundle", "type": "searchset", "total": 1, "entry": [{ "fullUrl": "https://api.service.nhs.uk/personal-demographics/FHIR/R4/Patient/9000000009", "search": { "score": 1 }, "resource": SEARCH_PATIENT_9000000009 }]
}
const WILDCARD_SEARCH = {
    "resourceType": "Bundle", "type": "searchset", "total": 2, "entry": [
        { "fullUrl": "https://api.service.nhs.uk/personal-demographics/FHIR/R4/Patient/9000000009", "search": { "score": 0.8343 }, "resource": SEARCH_PATIENT_9000000009 },
        { "fullUrl": "https://api.service.nhs.uk/personal-demographics/FHIR/R4/Patient/9000000017", "search": { "score": 0.8343 }, "resource": SEARCH_PATIENT_9000000017 }
    ]
}
const FUZZY_SEARCH_PATIENT_17 = {
    "resourceType": "Bundle", "type": "searchset", "total": 1, "entry": [{ "fullUrl": "https://api.service.nhs.uk/personal-demographics/FHIR/R4/Patient/9000000017", "search": { "score": 0.8976 }, "resource": SEARCH_PATIENT_9000000017 }]
}

/*
    Supporting functions for building responses
*/
function janeSmithSearchsetWithScore(score) {
    return {
        "resourceType": "Bundle",
        "type": "searchset",
        "total": 1,
        "entry": [
            {
                "fullUrl": "https://api.service.nhs.uk/personal-demographics/FHIR/R4/Patient/9000000009",
                "search": {"score": score},
                "resource": SEARCH_PATIENT_9000000009
            }
        ]
    }
}

/*
    Functions to handle error responses
*/
function invalidUpdateError(request, diagnostics) {
    let body = context.read('classpath:mocks/stubs/errorResponses/INVALID_UPDATE.json');
    body.issue[0].diagnostics = diagnostics;
    response.headers = basicResponseHeaders(request);
    response.body = body;
    response.status = 400;
    return false
}

/*
    Specific query param validation to support main handler
*/
function validateQueryParams(request) {
    const NOT_ENOUGH_SEARCH_PARAMS = "Not enough search parameters were provided for a valid search, you must supply family and birthdate as a minimum and only use recognised parameters from the api catalogue."

    const REQUIRED_PARAMS = [
        "family", "gender", "birthdate"
    ]
    const VALID_PARAMS = [
        "_fuzzy-match", "_exact-match", "_history", "_max-results", 
        "family", "given", "gender", "birthdate", "death-date", 
        "address-postcode", "general-practitioner", "email", "phone"
    ]
    
    // check the validity of certain params first
    const birthDateArray = request.params['birthdate']
    context.log("birthDateArray: " + birthDateArray)
    if (birthDateArray) {
        for (let i = 0; i < birthDateArray.length; i++) {
            const birthDate = birthDateArray[i]
            if (!birthDate || !birthDate.match(/^(eq|ne|gt|lt|ge|le)?[0-9]{4}-[0-9]{2}-[0-9]{2}$/)) {
                const diagnostics = `Invalid value - '${birthDate}' in field 'birthdate'`;
                return returnInvalidSearchDataError(diagnostics)
            }
        }
    }

    // ignore any params that we don't handle
    let validParams = [];
    for (let paramName in request.params) {
        context.log("paramName: " + paramName)
        if (VALID_PARAMS.includes(paramName)) {
            validParams.push(paramName)
        }
    }
    // then return an error if any of the required params are missing
    for (let i = 0; i < REQUIRED_PARAMS.length; i++) {
        if (!validParams.includes(REQUIRED_PARAMS[i])) {
            return returnMissingValueError(NOT_ENOUGH_SEARCH_PARAMS)
        }
    }

    return true
}

function otherJaneSmithParamsAreValid(request) {    
    if (request.param('phone') && request.param('phone') != "01632960587") return false
    if (request.param('email') && request.param('email') != "jane.smith@example.com") return false
    return true
}


/*
    Handler for search Patient functionality
*/
if (request.pathMatches('/Patient') && request.get) {
    response.headers = basicResponseHeaders(request)

    let valid = validateHeaders(request);
    if (valid) { valid = validateQueryParams(request) }

    const family = request.param('family')
    const given = request.params['given']
    const gender = request.param('gender')
    const birthDate = request.params['birthdate']
    const fuzzyMatch = request.paramBool('_fuzzy-match')
    const phone = request.param('phone')
    const email = request.param('email')

    if (valid) {
        if (fuzzyMatch) {
            if (!phone && !email) {
                response.body = FUZZY_SEARCH_PATIENT_17
            } else if (phone == "01632960587" && !email) {
                response.body = janeSmithSearchsetWithScore(0.9124)
            } else if (email == "jane.smith@example.com" && !phone) {
                response.body = janeSmithSearchsetWithScore(0.9124)
            } else if (phone == "01632960587" && email == "jane.smith@example.com") {
                response.body = janeSmithSearchsetWithScore(0.9542)
            }
        }
        else if (["Sm*", "sm*"].includes(family)) {
            if (!phone && !email) {
                response.body = WILDCARD_SEARCH
            } else if (phone == "01632960587" && !email) {
                response.body = janeSmithSearchsetWithScore(1)
            } else if (email == "jane.smith@example.com" && !phone) {
                response.body = janeSmithSearchsetWithScore(1)
            }
        }
        else if (["Smythe", "smythe"].includes(family)) {
            response.body = RESTRICTED_PATIENT_SEARCH
        }
        else if (["Smith", "smith"].includes(family) && ["Female", "female"].includes(gender) && (birthDate == "eq2010-10-22" || birthDate == "ge2010-10-21,le2010-10-23") && (otherJaneSmithParamsAreValid(request))) {
            response.body = SIMPLE_SEARCH
        }
        else if (["Smith", "smith"].includes(family) && ["Male", "male"].includes(gender) && given.length == 2) {
            response.body = COMPOUND_NAME_SEARCH
        }    
        else {
            response.body = EMPTY_SEARCHSET
        }
    }
}