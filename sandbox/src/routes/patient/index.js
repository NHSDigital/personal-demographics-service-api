const get = require('./get-patient');
const patch = require('./patch-patient');
const poll = require('./polling');

const routes = [].concat(get, patch, poll);

module.exports = routes;