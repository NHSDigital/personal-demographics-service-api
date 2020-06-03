'use strict'

const Hapi = require('@hapi/hapi')
const Path = require('path')
const Inert = require('inert')
const routes = require('./routes/patient')

const CONTENT_TYPE = 'application/fhir+json'

const preResponse = function (request, h) {
    const response = request.response

    // Don't reformat non-error responses, and don't reformat system (>=500) errors
    if (!response.isBoom) {
        let statusCode = response.statusCode
        if (statusCode != 202) {
            // Currently don't require a content-type on a 202 as there is no content.
            response.type(CONTENT_TYPE)
        }
        return h.continue
    }

    const error = response

    // Generically present all errors not explicitly thrown by
    // us as internal server errors
    if (!error.data) {
        error.data = {}
        error.data['apiErrorCode'] = "FAILURE_TO_PROCESS_MESSAGE"
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
    let severity = error.data.operationOutcomeSeverity
    if (!severity) {
        severity = "error"
    }

    const fhirError = {
        resourceType: "OperationOutcome",
        issue: [{
            severity: severity,
            code: error.data.operationOutcomeCode,
            details: {
                coding: [{
                    system: "https://fhir.nhs.uk/R4/CodeSystem/Spine-ErrorOrWarningCode",
                    version: "1",
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

    // Binding some variables to allow for persistence on the server.
    server.bind({
        messages: {}
    });

    server.ext('onPreResponse', preResponse);

    await server.register(Inert)

    server.route(routes)

    await server.start()
    console.log('Server running on %s', server.info.uri)
}

process.on('unhandledRejection', (err) => {
    console.log(err);
    process.exit(1);
})

init()
