/*
    Common constants
*/
const X_REQUEST_ID = "X-Request-ID";

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


function getParam(request, paramName) {
    // Get the value of the parameter, and convert it to lowercase if it's a string
    value = request.params[paramName]
    if (typeof value !== 'string') {
        return value
    } else {
        return value.toLowerCase()
    }
}

function basicResponseHeaders(request) {
    return {
        'content-type': 'application/fhir+json',
        'x-request-id': request.headers['x-request-id'],
        'x-correlation-id': request.headers['x-correlation-id']    
    } 
};

/*
    Validate the headers
*/
function validateHeaders(request) {
    var valid = true;

    const requestID = request.header('x-request-id')
    if (!requestID) {
        response.body = context.read('classpath:mocks/stubs/errorResponses/MISSING_VALUE_x-request-id.json')
        const headers = basicResponseHeaders(request)
        response.headers = headers
        response.status = 400
        valid = false
    } else if (!isValidUUID(requestID)) {
        valid = invalidValueError(X_REQUEST_ID, requestID, request)
    }
    return valid
}


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
    Common error response handlers
*/
function invalidValueError(field, value, request) {

    let body = context.read('classpath:mocks/stubs/errorResponses/INVALID_VALUE.json');
    body.issue[0].diagnostics = `Invalid value - '${value}' in header '${field}'`;
    response.body = body;
    response.headers = basicResponseHeaders(request);
    response.status = 400;
    return false
}


/*
    Response definitions
*/
function returnBundle(filename) {
    response.body = getTimestampedBody(`classpath:mocks/stubs/patientResponses/${filename}`)
    response.status = 200
}


function returnEmptyBundle() {
    response.body = getTimestampedBody('classpath:mocks/stubs/patientResponses/empty_bundle.json')
    response.status = 200
}


function returnMissingValueError(diagnostics) {
    let body = context.read('classpath:mocks/stubs/patient/errorResponses/missing_value.json')
    body["issue"][0]["diagnostics"] = diagnostics
    response.body = body
    response.status = 400
}


function returnTooManyMatchesError() {
    response.body = context.read('classpath:mocks/stubs/patient/errorResponses/too_many_matches.json')
    response.status = 400
}


function validateDate(dateString, field) {
    const regex=new RegExp("([0-9]{4}[-](0[1-9]|1[0-2])[-]([0-2]{1}[0-9]{1}|3[0-1]{1})|([0-2]{1}[0-9]{1}|3[0-1]{1})[-](0[1-9]|1[0-2])[-][0-9]{4})")
    const valid = regex.test(dateString)
    if (!valid) {
        const diagnostics = `Invalid value - '${dateString}' in field '${field}'`
        const body = context.read('classpath:stubs/patient/errorResponses/invalid_search_data.json')
        body['issue'][0]['diagnostics'] = diagnostics
        response.body = body
        response.status = 400
    }
}


context.read('classpath:mocks/get-patient-retrieve.js');
context.read('classpath:mocks/patch-patient.js');