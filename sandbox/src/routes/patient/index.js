const get = require('./get-patient');
const patch = require('./patch-patient');
const healthcheck = require('./healthcheck');

const routes = [].concat(get, patch, healthcheck);

module.exports = routes;
