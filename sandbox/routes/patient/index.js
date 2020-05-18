const get = require('./get-patient');
const patch = require('./patch-patient');
const _status = require('./_status')

const routes = [].concat(get, patch, _status);

module.exports = routes;
