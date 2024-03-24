function buildResponseHeaders(request, patient) {
    return {
        'content-type': 'application/fhir+json',
        'etag': `W/"${patient.meta.versionId}"`,
        'x-request-id': request.header('x-request-id'),
        'x-correlation-id': request.header('x-correlation-id')
    };
}

/*
    Diagnostics strings for error messages
*/
const NO_PATCHES_PROVIDED = "Invalid update with error - No patches found";
const INVALID_RESOURCE_ID = "Invalid update with error - This resource has changed since you last read. Please re-read and try again with the new version number.";

/*
    Functions to handle error responses
*/
function invalidUpdateError(diagnostics) {
    let body = context.read('classpath:mocks/stubs/errorResponses/INVALID_UPDATE.json');
    body.issue[0].diagnostics = diagnostics;
    response.body = body;
    response.status = 400;
    return false
}

function preconditionFailedError(diagnostics) {
    let body = context.read('classpath:mocks/stubs/errorResponses/PRECONDITION_FAILED.json');
    body.issue[0].diagnostics = diagnostics;
    response.body = body;
    response.status = 412;
    return false
}

/*
    The main logic for patching a patient
*/
function patchPatient(originalPatient, request) {
    let newPatient = JSON.parse(JSON.stringify(originalPatient));

    if (!request.body.patches) {
        return invalidUpdateError(NO_PATCHES_PROVIDED);
    }

    if (request.header('If-Match') != `W/"${originalPatient.meta.versionId}`) {
        return preconditionFailedError(INVALID_RESOURCE_ID);
    }


    for(let i = 0; i < request.body.patches.length; i++) {
        let patch = request.body.patches[i];
        if (patch.op == 'add' && patch.path === '/name/-') {
            newPatient.name.push(patch.value);
        }
        if (patch.op == 'replace' && patch.path === '/name/0/given/0') {
            newPatient.name[0].given[0] = patch.value;
        }
        if (patch.op == 'replace' && patch.path === '/gender') {
            newPatient.gender = patch.value;
        }
        if (patch.op == 'remove' && patch.path === '/name/0/suffix/0') {
            newPatient.name[0].suffix.splice(0, 1);
        }
    }
    newPatient.meta.versionId = (parseInt(newPatient.meta.versionId) + 1);
    return newPatient;
}

/*
    Handler for patch patient
*/
if (request.pathMatches('/Patient/{nhsNumber}') && request.patch) {

    const nhsNumber = request.pathParams.nhsNumber;
    let validNHSNumber = validate(nhsNumber)
    const requestID = request.header('x-request-id')
    let errors = false;

    if (!requestID) {
        errors = true
        response.body = context.read('classpath:mocks/stubs/errorResponses/MISSING_VALUE_x-request-id.json')
        response.status = 400
    } else if (!isValidUUID(requestID)) {
        errors = true
        invalidValueError(X_REQUEST_ID, requestID)
    } else if (!validNHSNumber) {
        errors = true
        response.body = context.read('classpath:stubs/oldSandbox/errors/INVALID_RESOURCE_ID.json');
        response.status = 400
    } else if (typeof session.patients[nhsNumber] == 'undefined') {
        errors = true
        response.body = context.read('classpath:stubs/oldSandbox/errors/RESOURCE_NOT_FOUND.json');
        response.status = 404
    } 
 
    if (!errors) {
        originalPatient = session.patients[nhsNumber]
        newPatient = patchPatient(originalPatient, request);
        if (newPatient) {
            session.patients[nhsNumber] = newPatient;
            response.headers = buildResponseHeaders(request, newPatient);
            response.body = newPatient;
            response.status = 200;
        }
    }
}
