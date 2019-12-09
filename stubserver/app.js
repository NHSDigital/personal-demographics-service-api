'use strict'

const Hapi = require('@hapi/hapi')
const Path = require('path')
const Inert = require('inert')
const Joi = require('@hapi/joi')
const Boom = require('boom')
const fs = require('fs')
const NhsNumberValidator = require('nhs-number-validator')

const EXAMPLE_PATIENT = JSON.parse(fs.readFileSync('mocks/Patient.json'))

const nhsNumberSchema = Joi.string().custom(function (value) {
    if (NhsNumberValidator.validate(value)) {
        return value
    }
    throw new Error('Invalid NHS Number')
}, 'NHS Number Validator')

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

    await server.register(Inert)

    server.route({
        method: 'GET',
        path: '/Patient/{nhsNumber}',
        handler: (request, h) => {
            // Validate NHS number is valid format
            // Ideally should be done using options.validate object (https://hapi.dev/tutorials/validation/)
            // But don't know how to customise the returned JSON when done this way
            const validationResult = nhsNumberSchema.validate(request.params.nhsNumber)
            if (validationResult.error) {
                const error = Boom.badRequest()
                error.output.payload = {
                    code: "invalid_nhs_number",
                    message: "NHS number is not in the correct format, or is not a real NHS number"
                }
                throw error
            }

            // Validate NHS number is for our test patient
            if (request.params.nhsNumber != EXAMPLE_PATIENT.nhs_number) {
                const error = Boom.notFound()
                error.output.payload = {
                    code: "not_found",
                    message: `Patient with NHS number ${request.params.nhsNumber} could not be found`
                }
                throw error
            }

            return h.response(EXAMPLE_PATIENT)
                .etag(EXAMPLE_PATIENT._version, { weak: true })
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