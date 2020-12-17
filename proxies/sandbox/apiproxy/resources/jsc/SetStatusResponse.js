var apiproxy_revision = context.getVariable('apiproxy.revision');

var sandbox_response_code = context.getVariable('sandboxHealthcheckResponse.status.code');
var sanbox_response = context.getVariable('sandboxHealthcheckResponse.content');
var sandbox_request_url = context.getVariable('sandboxHealthcheckRequest.url');

var sandbox_request_has_failed = context.getVariable("servicecallout.ServiceCallout.CallSandboxHealthcheck.failed");

var sandbox_status = "fail";

if (sandbox_response_code / 100 == 2) {
  sandbox_status = "pass";
}

timeout = "false";

if (sandbox_response_code === null && sandbox_request_has_failed) {
  timeout = "true";
}



var sandbox_service = {
  "sandbox:status": [{
    "status": sandbox_status,
    "timeout": timeout,
    "responseCode": sandbox_response_code,
    "outcome": sanbox_response,
    "links": { "self": sandbox_request_url }
  }]
};

var apigee_status = "pass";

if (sandbox_status != "pass") {
  apigee_status = "fail";
}



var response = {
  "status": apigee_status,
  "version": "{{ DEPLOYED_VERSION }}",
  "revision": apiproxy_revision,
  "releaseId": "{{ RELEASE_RELEASEID }}",
  "commitId": "{{ SOURCE_COMMIT_ID }}",
  "checks": sandbox_service
};

context.setVariable("status.response", JSON.stringify(response));
context.setVariable("response.content", JSON.stringify(response));
context.setVariable("response.header.Content-Type", "application/json");
