# OAuth API Proxy

Temporary home for this proxy until it gets it's own repository, pipeline, etc.

## Pre-Requisites

### Identity Provider Registration

This proxy must be registered as an 'Application' with the Identity Provider.

You must supply the callback URL (redirect URI): `https://<environment_hostname>.<proxy_base_path>/callback`

You will receive:
 * `client_id`
 * `client_secret`
 * OAuth endpoint URIs
   * Authorize endpoint
   * Access token endpoint

### Apigee Environment Configuration

Following must be present for each deployed environment:

* Cache `client-state` - 5 minute expiry
* Target Server `identity-server` - Identity Provider's OAuth server
* Key-Value Map `oauth-credentials` (recommend encrypted) with following items:
  * `client_id` (as above)
  * `client_secret` (as above)
  * `redirect_uri` (as above)
  * `authorize_endpoint` Full URI (including scheme) of Identity provider's 'Authorize' endpoint. e.g. `https://identity.server.com/path/to/authorize`
  * `access_token_path` The *Path* component of the access token endpoint at the identity server. e.g. `/some/path/to/access_token`
