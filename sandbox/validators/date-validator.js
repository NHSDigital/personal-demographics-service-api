const Joi = require('@hapi/joi')

module.exports = {
    dateSchema: Joi.string().pattern(/^\d{4}-\d{2}-\d{2}$/),
    birthdateSchema: Joi.string().pattern(/^[a-z]{2}\d{4}-\d{2}-\d{2}$/)
}