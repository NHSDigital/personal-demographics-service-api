client_id = context.getVariable('request.queryparam.client_id');
state = context.getVariable('request.queryparam.state');
redirect_uri = context.getVariable('request.queryparam.redirect_uri');
response_type = context.getVariable('request.queryparam.response_type');
scope = context.getVariable('request.queryparam.scope');

var cacheEntry = {
  client_id: client_id,
  redirect_uri: redirect_uri,
  state: state,
  response_type: response_type,
  scope: scope
};

context.setVariable('cacheEntry', JSON.stringify(cacheEntry));
