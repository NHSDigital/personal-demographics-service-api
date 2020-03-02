const get = require('./get-patient');
const patch = require('./patch-patient');

const routes = [].concat(get, patch);

module.exports = routes;