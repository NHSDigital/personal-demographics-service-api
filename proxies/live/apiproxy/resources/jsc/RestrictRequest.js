const isRequestRestricted = require('isRequestRestricted')

var method_is_restricted = isRequestRestricted.is_request_restricted();
context.setVariable('apigee.method_is_restricted', method_is_restricted);