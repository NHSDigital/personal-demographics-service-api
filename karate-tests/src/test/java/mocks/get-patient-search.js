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
    Diagnostics strings
*/
const NOT_ENOUGH_SEARCH_PARAMS = "Not enough search parameters were provided for a valid search, you must supply family and birthDate as a minimum and only use recognised parameters from the api catalogue."


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
function otherJaneSmithParamsAreValid(request) {    
    if (request.param('phone') && request.param('phone') != "01632960587") {
        context.log("phone: " + request.param('phone'))
        return false
    }
    if (request.param('email') && request.param('email') != "jane.smith@example.com") {
        context.log("email: " + request.param('email'))
        return false
    }
    return true
    // const exactMatch = request.param('_exact-match')
    // const history = request.param('history')
    // const maxResults = request.param('_max-results')
    // const given = request.param('given')
    // const deathDate = request.param('death-date')
    // const postalCode = request.param('address-postcode');
    // const gp = request.param('general-practitioner')
}


/*
    Handler for search Patient functionality
*/
if (request.pathMatches('/Patient') && request.get) {

    let valid = validateHeaders(request);
    response.headers = basicResponseHeaders(request)

    const paramsCount = Object.keys(request.params).length
    if (paramsCount == 0) {
        returnMissingValueError(NOT_ENOUGH_SEARCH_PARAMS, request)
    }

    const family = request.param('family')
    const given = request.params['given']
    context.log("given: " + given)
    context.log(given == ["John Paul","James"])
    const gender = request.param('gender')
    const birthDate = request.params['birthdate']
    const fuzzyMatch = request.paramBool('_fuzzy-match')
    const phone = request.param('phone')
    const email = request.param('email')

    // context.log(request.params)
    if (!valid) {
        response.body = "not valid"
        response.status = 401
    }
    else if (fuzzyMatch) {
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