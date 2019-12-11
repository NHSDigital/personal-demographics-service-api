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

const dateSchema = Joi.string().pattern(/^\d{4}-\d{2}-\d{2}$/)

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
            if (request.params.nhsNumber != EXAMPLE_PATIENT.id) {
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
                "general-practicioner": true,
            };

            // If provided, validate birthdate, death-date params
            // TODO: birthdate range
            ["birthdate", "death-date"].forEach(dateParam => {
                if (request.query[dateParam] && dateSchema.validate(request.query[dateParam]).error) {
                    const error = Boom.badRequest()
                    error.output.payload = {
                        code: "invalid_search_params",
                        message: `${dateParam} has invalid format: ${request.query[dateParam]} is not in YYYY-MM-DD format`
                    }
                    throw error
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
                const error = Boom.badRequest()
                error.output.payload = {
                    code: "invalid_search_params",
                    message: "Not enough search parameters were provided to be able to make a search"
                }
                throw error
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
                if (request.query[p] !== simpleSearchParams[p]) {
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

    await server.start()
    console.log('Server running on %s', server.info.uri)
}

process.on('unhandledRejection', (err) => {
    console.log(err);
    process.exit(1);
})

init()