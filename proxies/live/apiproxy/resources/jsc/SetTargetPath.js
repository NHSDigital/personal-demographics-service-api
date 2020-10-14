var proxy_pathsuffix = context.getVariable('proxy.pathsuffix');
var targetPath = "";

if (proxy_pathsuffix == "/_status") {
    targetPath = "/healthcheck";
    context.setVariable('target.copy.pathsuffix', false);
}

context.setVariable("targetPath", targetPath);
