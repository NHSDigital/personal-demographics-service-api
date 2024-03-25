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
const NO_IF_MATCH_HEADER = "Invalid update with error - If-Match header must be supplied to update this resource";
const NO_PATCHES_PROVIDED = "Invalid update with error - No patches found";
const INVALID_RESOURCE_ID = "Invalid update with error - This resource has changed since you last read. Please re-read and try again with the new version number.";
const INVALID_PATCH = "Invalid patch: Operation `op` property is not one of operations defined in RFC-6902"

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

function unsupportedServiceError() {
    let body = context.read('classpath:mocks/stubs/errorResponses/UNSUPPORTED_SERVICE.json');
    response.body = body;
    response.status = 400;
    return false
}

/*
    Validate the headers specific to patching a patient
*/
function validatePatchHeaders(request) {
    var valid = true;
    if (!request.header('If-Match')) {
        valid = preconditionFailedError(NO_IF_MATCH_HEADER)
    } else if (!request.header('Content-Type').includes('application/json-patch+json')) {
        valid = unsupportedServiceError()
    }
    return valid
}



/*
    The main logic for patching a patient
*/
function patchPatient(originalPatient, request) {

    if (!request.body.patches) {
        return invalidUpdateError(NO_PATCHES_PROVIDED);
    }
    if (request.header('If-Match') != `W/"${originalPatient.meta.versionId}"`) {
        return preconditionFailedError(INVALID_RESOURCE_ID);
    }

    let updatedPatient = JSON.parse(JSON.stringify(originalPatient));
    const validOperations = ['add', 'replace', 'remove', 'test']
    for(let i = 0; i < request.body.patches.length; i++) {
        let patch = request.body.patches[i];    
        if (validOperations.indexOf(patch.op) == -1) {
            return invalidUpdateError(INVALID_PATCH)
        }
        if (patch.op == 'add' && patch.path === '/name/-') {
            updatedPatient.name.push(patch.value);
        }
        if (patch.op == 'replace' && patch.path === '/name/0/given/0') {
            updatedPatient.name[0].given[0] = patch.value;
        }
        if (patch.op == 'replace' && patch.path === '/gender') {
            updatedPatient.gender = patch.value;
        }
        if (patch.op == 'replace' && patch.path.startsWith('/address/0')) {
            return invalidUpdateError("Invalid update with error - no id or url found for path with root /address/0");
        }
        if (patch.op == 'remove' && patch.path === '/name/0/suffix/0') {
            updatedPatient.name[0].suffix.splice(0, 1);
        }
    }
    updatedPatient.meta.versionId = (parseInt(updatedPatient.meta.versionId) + 1);
    return updatedPatient;
}

/*
    Handler for patch patient
*/
if (request.pathMatches('/Patient/{nhsNumber}') && request.patch) {

    let valid = validateNHSNumber(request) && validateHeaders(request) && validatePatchHeaders(request);

    if (valid) {
        const nhsNumber = request.pathParams.nhsNumber;    
        const originalPatient = session.patients[nhsNumber];
        let updatedPatient = patchPatient(originalPatient, request);
        if (updatedPatient) {
            session.patients[nhsNumber] = updatedPatient;
            response.headers = buildResponseHeaders(request, updatedPatient);
            response.body = updatedPatient;
            response.status = 200;
        }
    }
}
