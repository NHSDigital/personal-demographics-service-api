/*
    Supporting functions
*/
// reading this file gives us the `validate` function for validating NHS numbers
context.read('classpath:helpers/nhs-number-validator.js');

function getTimestampedBody(pathToBody) {
    let body = context.read(pathToBody)
    body['timestamp'] = new Date().toISOString()
    return body
}

function isValidUUID(uuid) {
    const regex = new RegExp("[0-9a-f]{8}-[0-9a-f]{4}-[0-5][0-9a-f]{3}-[089ab][0-9a-f]{3}-[0-9a-f]{12}")
    return regex.test(uuid)
}

function basicResponseHeaders(request) {
    return {
        'content-type': 'application/fhir+json',
        'x-request-id': request.headers['x-request-id'],
        'x-correlation-id': request.headers['x-correlation-id']    
    } 
};


function validateNHSNumber(request) {
    const nhsNumber = request.pathParams.nhsNumber;
    let valid = true;
    let validNHSNumber = validate(nhsNumber)
    if (!validNHSNumber) {
        valid = false
        response.headers = basicResponseHeaders(request)
        response.body = context.read('classpath:mocks/stubs/errorResponses/INVALID_RESOURCE_ID.json');
        response.status = 400
    } else if (typeof session.patients[nhsNumber] == 'undefined') {
        valid = false
        response.headers = basicResponseHeaders(request)
        response.body = context.read('classpath:mocks/stubs/errorResponses/RESOURCE_NOT_FOUND.json');
        response.status = 404
    }
    return valid;
}


/*
    Error responses
*/
function returnInvalidValueError(field, value, request) {

    let body = context.read('classpath:mocks/stubs/errorResponses/INVALID_VALUE.json');
    body.issue[0].diagnostics = `Invalid value - '${value}' in header '${field}'`;
    response.body = body;
    response.headers = basicResponseHeaders(request);
    response.status = 400;
    return false
}

function returnMissingValueError(diagnostics) {
    let body = context.read('classpath:mocks/stubs/errorResponses/MISSING_VALUE.json')
    body["issue"][0]["diagnostics"] = diagnostics
    response.body = body
    response.status = 400
    return false
}


function returnInvalidSearchDataError(diagnostics) {
    let body = context.read('classpath:mocks/stubs/errorResponses/INVALID_SEARCH_DATA.json')
    body["issue"][0]["diagnostics"] = diagnostics
    response.body = body
    response.status = 400
    return false
}


/*
    Validate the headers
*/
function validateHeaders(request) {
    const X_REQUEST_ID = "X-Request-ID";

    var valid = true;

    const requestID = request.header('x-request-id')
    if (!requestID) {
        const diagnostics = "Invalid request with error - X-Request-ID header must be supplied to access this resource"
        valid = returnMissingValueError(diagnostics)
    } else if (!isValidUUID(requestID)) {
        valid = returnInvalidValueError(X_REQUEST_ID, requestID, request)
    }
    return valid
}


/*
    Load all the specific mocks
*/
context.read('classpath:mocks/get-patient-retrieve.js');
context.read('classpath:mocks/get-patient-search.js');
context.read('classpath:mocks/patch-patient.js');