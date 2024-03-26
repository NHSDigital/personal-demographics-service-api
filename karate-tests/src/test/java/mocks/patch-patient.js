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
function invalidUpdateError(request, diagnostics) {
    let body = context.read('classpath:mocks/stubs/errorResponses/INVALID_UPDATE.json');
    body.issue[0].diagnostics = diagnostics;
    response.headers = basicResponseHeaders(request);
    response.body = body;
    response.status = 400;
    return false
}

function preconditionFailedError(request, diagnostics) {
    let body = context.read('classpath:mocks/stubs/errorResponses/PRECONDITION_FAILED.json');
    body.issue[0].diagnostics = diagnostics;
    response.headers = basicResponseHeaders(request);
    response.body = body;
    response.status = 412;
    return false
}

function unsupportedServiceError(request) {
    let body = context.read('classpath:mocks/stubs/errorResponses/UNSUPPORTED_SERVICE.json');
    response.headers = basicResponseHeaders(request);
    response.body = body;
    response.status = 400;
    return false
}

/*
    Validate the headers specific to patching a patient
*/
function validatePatchHeaders(request) {
    var valid = true;
    if (!request.header('if-match')) {
        valid = preconditionFailedError(request, NO_IF_MATCH_HEADER)
    }
    if (valid && !request.header('content-type').startsWith('application/json-patch+json')) {
        valid = unsupportedServiceError(request)
    }
    return valid
}

/*
    The main logic for patching a patient
*/
function patchPatient(originalPatient, request) {

    if (!request.body.patches) {
        return invalidUpdateError(request, NO_PATCHES_PROVIDED);
    }
    if (request.header('if-match') != `W/"${originalPatient.meta.versionId}"`) {
        return preconditionFailedError(request, INVALID_RESOURCE_ID);
    }

    let updatedPatient = JSON.parse(JSON.stringify(originalPatient));
    let updateErrors = [];

    const validOperations = ['add', 'replace', 'remove', 'test']
    for(let i = 0; i < request.body.patches.length; i++) {
        let patch = request.body.patches[i];    
        if (validOperations.indexOf(patch.op) == -1) {
            return invalidUpdateError(request, INVALID_PATCH)
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
        if (patch.op == 'remove' && patch.path === '/name/0/suffix/0') {
            updatedPatient.name[0].suffix.splice(0, 1);
        }

        // these specific error scenarios for update errors should be reviewed
        if (patch.op == 'replace' && patch.path === "/address/0/line/0" && patch.value === "2 Whitehall Quay") {
            updateErrors.push("Invalid update with error - no id or url found for path with root /address/0");
        } else if (patch.op == 'replace' && patch.path.startsWith("/address/0/") && !originalPatient.hasOwnProperty('address')) {
            updateErrors.push("Invalid update with error - Invalid patch - index '0' is out of bounds");
        } else if (patch.op == 'replace' && patch.path === "/address/0/id" && patch.value === "456") {
            updateErrors.push("Invalid update with error - no 'address' resources with object id 456");
        } else if (patch.op == 'replace' && patch.path === "/address/0/line") {
            updateErrors.push("Invalid update with error - Invalid patch - can't replace non-existent object 'line'");
        } else if (patch.op == 'replace' && patch.path === "/address/0/id" && patch.value === "123456") {
            updateErrors.push("Invalid update with error - no 'address' resources with object id 123456");
        }
    }

    // why is it that for this specific scenario (Invalid patch - attempt to replace non-existent object), 
    // we have to pick the last error message, when for all the others we pick the first error message?
    const rogueErrors = [
        "Invalid update with error - no 'address' resources with object id 456",
        "Invalid update with error - Invalid patch - can't replace non-existent object 'line'"
    ]

    if (updateErrors.length > 0) {
        if (updateErrors.every(item => rogueErrors.includes(item)) && rogueErrors.every(item => updateErrors.includes(item))) {
            return invalidUpdateError(request, updateErrors[1])
        } else {
            return invalidUpdateError(request, updateErrors[0])
        }
    } else {
        updatedPatient.meta.versionId = (parseInt(updatedPatient.meta.versionId) + 1);
        return updatedPatient;
    }
}

/*
    Handler for patch patient
*/
if (request.pathMatches('/Patient/{nhsNumber}') && request.patch) {
    const valid = validateNHSNumber(request) && validatePatchHeaders(request) && validateHeaders(request)
    if (valid) {
        const nhsNumber = request.pathParams.nhsNumber;    
        const originalPatient = session.patients[nhsNumber];
        let updatedPatient = patchPatient(originalPatient, request);
        if (updatedPatient) {
            // this line is commented out because the existing tests assume a stateless mock
            // session.patients[nhsNumber] = updatedPatient;
            response.headers = buildResponseHeaders(request, updatedPatient);
            response.body = updatedPatient;
            response.status = 200;
        }
    }
}
