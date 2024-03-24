/*
    Supporting functions
*/
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
        console.log(`${value} is not a string`)
        return value
    } else {
        return value.toLowerCase()
    }
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
context.read('classpath:mocks/get-patient-search.js');
context.read('classpath:mocks/patch-patient.js');