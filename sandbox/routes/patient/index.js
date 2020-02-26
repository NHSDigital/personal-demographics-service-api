let get = require('./get-patient');
let patch = require('./patch-patient');

let routes = [].concat(get, patch);

module.exports = routes;