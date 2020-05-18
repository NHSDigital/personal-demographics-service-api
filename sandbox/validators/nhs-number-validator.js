const Joi = require('@hapi/joi')
const NhsNumberValidator = require('nhs-number-validator')

module.exports = {
    nhsNumberSchema: Joi.string().custom(function (value) {
        if (NhsNumberValidator.validate(value)) {
            return value
        }
        throw new Error('Invalid NHS Number')
    }, 'NHS Number Validator') 
}