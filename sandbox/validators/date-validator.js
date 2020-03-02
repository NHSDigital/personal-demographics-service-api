const Joi = require('@hapi/joi')

module.exports = {
    dateSchema: Joi.string().pattern(/^[a-z]{2}\d{4}-\d{2}-\d{2}$/)
}