const get = require('./get-patient');
const patch = require('./patch-patient');
const poll = require('./polling');
const healthcheck = require('./healthcheck');

const routes = [].concat(get, patch, poll, healthcheck);

module.exports = routes;
