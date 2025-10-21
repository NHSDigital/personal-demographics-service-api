const apiproxy_revision = context.getVariable('apiproxy.revision');

const sandbox_response_code = context.getVariable('sandboxHealthcheckResponse.status.code');
const sandbox_request_url = context.getVariable('sandboxHealthcheckRequest.url');

const sandbox_request_has_failed = context.getVariable("servicecallout.ServiceCallout.CallSandboxHealthcheck.failed");

let sandbox_status = "fail";

if (sandbox_response_code / 100 == 2) {
  sandbox_status = "pass";
}

let timeout = "false";

if (sandbox_response_code === null && sandbox_request_has_failed) {
  timeout = "true";
}

function json_tryparse(raw) {
  try {
      return JSON.parse(raw);
  }
  catch (e) {
      return raw;
  }
}

const sanbox_response = json_tryparse(context.getVariable('sandboxHealthcheckResponse.content'));

const sandbox_service = {
  "sandbox:status": [{
    "status": sandbox_status,
    "timeout": timeout,
    "responseCode": sandbox_response_code,
    "outcome": sanbox_response,
    "links": { "self": sandbox_request_url }
  }]
};

let apigee_status = "pass";

if (sandbox_status != "pass") {
  apigee_status = "fail";
}



const response = {
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
