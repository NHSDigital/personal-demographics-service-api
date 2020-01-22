'use strict'


const Hapi = require('@hapi/hapi')
const Path = require('path')
const Inert = require('inert')
const Joi = require('@hapi/joi')
const Boom = require('boom')
const fs = require('fs')
const NhsNumberValidator = require('nhs-number-validator')
const jsonpatch = require('fast-json-patch')

const EXAMPLE_PATIENT = JSON.parse(fs.readFileSync('mocks/Patient.json'))
const CONTENT_TYPE = 'application/fhir+json; fhirVersion=4.0'

const nhsNumberSchema = Joi.string().custom(function (value) {
    if (NhsNumberValidator.validate(value)) {
        return value
    }
    throw new Error('Invalid NHS Number')
}, 'NHS Number Validator')

const dateSchema = Joi.string().pattern(/^\d{4}-\d{2}-\d{2}$/)

/**
 * Used by Patient/{nhsNumber} paths to check it has been supplied in
 * correct format, and is the NHS Number of our example Patient record
 *
 * Returns nothing.
 *
 * Throws an appropriate Boom error message if either of these are wrong
 *
 * @param {*} request - hapi's request object
 */
const checkNhsNumber = function (request) {
    // Validate NHS number is valid format
    // Ideally should be done using options.validate object (https://hapi.dev/tutorials/validation/)
    // But don't know how to customise the returned JSON when done this way
    const validationResult = nhsNumberSchema.validate(request.params.nhsNumber)
    if (validationResult.error) {
        throw Boom.badRequest(
            `NHS Number ${request.params.nhsNumber} is not a valid NHS number`,
            {operationOutcomeCode: "value", apiErrorCode: "invalidNHSNumber"})
    }

    // Validate NHS number is for our test patient
    if (request.params.nhsNumber != EXAMPLE_PATIENT.id) {
        throw Boom.notFound(
            `Patient with NHS number ${request.params.nhsNumber} could not be found`,
            {operationOutcomeCode: "not_found", apiErrorCode: "patientNotFound"}
        )
    }
}


/**
 * Helper method to prepare a response for a FHIR resource JSON object
 *
 * @param {*} h hapi response toolkit
 * @param {*} resource FHIR resource object having meta.versionId property
 * @returns hapi response
 */
const createFhirResponse = function(h, resource) {
    return h.response(resource)
        .etag(resource.meta.versionId, { weak: true })
}

const preResponse = function (request, h) {
    const response = request.response

    // Don't reformat non-error responses, and don't reformat system (>=500) errors
    if (!response.isBoom ) {
        // Set Content-Type on all responses
        response.type(CONTENT_TYPE)
        return h.continue
    }

    const error = response

    // Generically present all errors not explicitly thrown by
    // us as internal server errors
    if (!error.data) {
        error.data = {}
        error.data['apiErrorCode'] = "internalServerError"
        error.data['operationOutcomeCode'] = "exception"
    }

    /* Reformat errors to FHIR spec
     Expects request.response is a Boom object with following properties:
      * Boom Standard:
        * message: human-readable error message
        * output.statusCode: HTTP status code
      * Custom:
        * data.operationOutcomeCode: from the [IssueType ValueSet](https://www.hl7.org/fhir/valueset-issue-type.html)
        * data.apiErrorCode: Our own code defined for each particular error. Refer to OAS.
    */
    const fhirError = {
        resourceType: "OperationOutcome",
        issue: [{
            severity: "error",
            code: error.data.operationOutcomeCode,
            details: {
                coding: [{
                    system: "https://my.spec.nhs.net/mycodingsystem",
                    version: 1,
                    code: error.data.apiErrorCode,
                    display: error.message
                }]
            }
        }]
    }

    return h.response(fhirError)
        .code(error.output.statusCode)
        .type(CONTENT_TYPE)
}

const init = async () => {
    const server = Hapi.server({
        port: 9000,
        host: '0.0.0.0',
        routes: {
            cors: true,  // Won't run as Apigee hosted target without this
            files: {
                relativeTo: Path.join(__dirname, 'mocks')
            }
        }
    })
    server.ext('onPreResponse', preResponse);

    await server.register(Inert)

    server.route({
        method: 'GET',
        path: '/Patient/{nhsNumber}',
        handler: (request, h) => {
            checkNhsNumber(request)
            return createFhirResponse(h, EXAMPLE_PATIENT)
        }
    })

    /* Patient search
        Behaviour implemented:
         * Provide no recognised search params: 400 + Appropriate error
         * Provide improperly-specified birthdate/death-date param: 400 + Appropriate error
         * Provide *some* search params: Empty search response
         * Provide ?birthdate=2010-10-22&family=Smith&given=Jane&gender=female: receive example patient as search result
    */
    server.route({
        method: 'GET',
        path: '/Patient',
        handler: (request, h) => {
            // TODO: This can be provided to a PatientSearcher to use to implement a more
            // 'proper' search
            const searchMap = {
                family: '$.name[?(@.use="usual")].family', // Usual family name
                given: true,
                gender: true,
                birthdate: true,
                "death-date": true,
                "address-postcode": true,
                organisation: true,
            };

            // If provided, validate birthdate, death-date params
            // TODO: birthdate range
            ["birthdate", "death-date"].forEach(dateParam => {
                if (request.query[dateParam] && dateSchema.validate(request.query[dateParam]).error) {
                    throw Boom.badRequest(
                        `${dateParam} has invalid format: ${request.query[dateParam]} is not in YYYY-MM-DD format`,
                        {operationOutcomeCode: "value", apiErrorCode: "invalidDateFormat"})
                }

            });

            // Check for too few search params
            // TODO: Improve this - currently checks for *any* search param
            let hasAnySearchParam = false
            for (let p of Object.keys(searchMap)) {
                if (request.query[p]) {
                    hasAnySearchParam = true
                    break
                }
            }
            if (!hasAnySearchParam) {
                throw Boom.badRequest(
                    "Not enough search parameters were provided to be able to make a search",
                    {operationOutcomeCode: "required", apiErrorCode: "tooFewSearchParams"})
            }

            // Build our empty search response
            let response = {
                resourceType: "Bundle",
                type: "searchset",
                timestamp: Date.now(),
                total: 0,
                entry: []
            }

            // Perform a 'simple search'
            const simpleSearchParams = {
                family: "Smith",
                given: "Jane",
                gender: "female",
                birthdate: "2010-10-22",
            }
            let simpleMatch = true
            for (let p of Object.keys(simpleSearchParams)) {
                if (!request.query[p] || request.query[p].toLowerCase() !== simpleSearchParams[p].toLowerCase()) {
                    simpleMatch = false
                    break
                }
            }
            // If so, try it
            if (simpleMatch) {
                response.total = 1
                response.entry.push({
                    search: {
                        score: 1.0
                    },
                    resource: EXAMPLE_PATIENT,
                })
            }

            return response
        }
    })

    /*
        Patient partial update
        Behaviour:
          * No If-Match Header: 400 DONE
          * If-Match header does not match resource latest: 412 Precondition Failed DONE
          * Invalid request body: 400(?)
          * Non-existant patient: 404 DONE
          * Invalid NHS Number: 400 DONE
          * Unset/invalid Content-Type: 415 Unsupported Media Type DONE
    */
    server.route({
        method: 'PATCH',
        path: '/Patient/{nhsNumber}',
        handler: (request, h) => {
            checkNhsNumber(request)

            // Check If-Match header exists
            // TODO: Return different error where If-Match header is incorrect format
            if (
                !request.headers["if-match"] ||
                !(request.headers["if-match"].startsWith('W/"') && request.headers["if-match"].endsWith('"'))) {
                throw Boom.badRequest(
                    "If-Match header must be supplied to update this resource",
                    {operationOutcomeCode: "required", apiErrorCode: "versionNotSupplied"}
                )
            }

            // Check If-Match header is correct version
            const ifMatch = request.headers["if-match"].slice(3, -1) // Strip the W/"..."
            if (ifMatch != EXAMPLE_PATIENT.meta.versionId) {
                throw Boom.preconditionFailed(
                    "This resource has changed since you last read. Please re-read and try again with the new version number.",
                    {operationOutcomeCode: "conflict", apiErrorCode: "versionMismatch"})
            }

            // Check Content-Type header
            if (!request.headers["content-type"]
                || request.headers["content-type"].toLowerCase() !== "application/json-patch+json") {
                // TODO: What's the proper error here?
                throw Boom.unsupportedMediaType(
                    "Must be application/json-patch+json",
                    {operationOutcomeCode: "value", apiErrorCode: "unsupportedMediaType"})
            }

            // Verify at least one patch object has been submitted
            if (!request.payload || !request.payload.patches || request.payload.patches.length === 0) {
                // TODO: Proper error message
                throw Boom.badRequest(
                    "No patches submitted",
                    {operationOutcomeCode: "required", apiErrorCode: "noPatchesSubmitted"})
            }

            // Apply the submitted patches
            let patchedPatient
            try {
                patchedPatient = jsonpatch.applyPatch(EXAMPLE_PATIENT, request.payload.patches, true, false).newDocument
            }
            catch (e) {
                const patchingError = e.message.slice(0, e.message.indexOf('\n')) // Just the first line; rest is tons of extraneous detail
                throw Boom.badRequest(
                    `Invalid patch: ${patchingError}`,
                    {operationOutcomeCode: "value", apiErrorCode: "invalidPatchOperation"})
            }
            patchedPatient.meta.versionId++

            return createFhirResponse(h, patchedPatient)
        }
    })


    await server.start()
    console.log('Server running on %s', server.info.uri)
}

process.on('unhandledRejection', (err) => {
    console.log(err);
    process.exit(1);
})

init()