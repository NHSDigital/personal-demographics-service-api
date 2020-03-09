var1 = context.getVariable('request.queryparam.client_id');
var2 = context.getVariable('request.queryparam.state');
var3 = context.getVariable('request.queryparam.redirect_uri');
var4 = context.getVariable('request.queryparam.response_type');
var5 = context.getVariable('request.queryparam.scope');

var cacheEntry = {
  client_id: var1,
  redirect_uri: var3,
  state: var2,
  response_type: var4,
  scope: var5
};

context.setVariable('cacheEntry', JSON.stringify(cacheEntry));
