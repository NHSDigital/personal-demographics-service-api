'use strict'

const Hapi = require('@hapi/hapi')
const Path = require('path')
const Inert = require('inert')

const CONTENT_TYPE = 'application/fhir+json; fhirVersion=4.0'

const preResponse = function (request, h) {
    const response = request.response

    // Don't reformat non-error responses, and don't reformat system (>=500) errors
    if (!response.isBoom) {
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
                    system: "https://fhir.nhs.uk/R4/CodeSystem/Spine-ErrorOrWarningCode",
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

const init = async() => {
    const server = Hapi.server({
        port: 9000,
        host: '0.0.0.0',
        routes: {
            cors: true, // Won't run as Apigee hosted target without this
            files: {
                relativeTo: Path.join(__dirname, 'mocks')
            }
        }
    })
    server.ext('onPreResponse', preResponse);

    await server.register(Inert)

    var routes = require('./routes/patient')
    server.route(routes)

    await server.start()
    console.log('Server running on %s', server.info.uri)
}

process.on('unhandledRejection', (err) => {
    console.log(err);
    process.exit(1);
})

init()
