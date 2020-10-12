var proxy_pathsuffix = context.getVariable('proxy.pathsuffix');
var targetBasePath = "";

if (proxy_pathsuffix == "/_status") {
    targetBasePath = "/healthcheck";
    context.setVariable('target.copy.pathsuffix', false);
}

context.setVariable("targetBasePath", targetBasePath);
