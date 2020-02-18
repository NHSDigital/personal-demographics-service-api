# personal-demographics-service-api

![Build](https://github.com/NHSDigital/personal-demographics-service-api/workflows/Build/badge.svg?branch=master)

This is a RESTful HL7® FHIR® API specification for the *Personal Demographics Service*.

* `specification/` This [Open API Specification](https://swagger.io/docs/specification/about/) describes the endpoints, methods and messages exchanged by the API. Use it to generate interactive documentation; the contract between the API and its consumers.
* `sandbox/` This NodeJS application implements a mock implementation of the service. Use it as a back-end service to the interactive documentation to illustrate interactions and concepts. It is not intended to provide an exhaustive/faithful environment suitable for full development and testing.
* `scripts/` Utilities helpful to developers of this specification.
* `apiproxy/` The Apigee API Proxy

Consumers of the API will find developer documentation on the [NHS Digital Developer Hub](https://emea-demo8-nhsdportal.apigee.io/).

## Contributing
Contributions to this project are welcome from anyone, providing that they conform to the [guidelines for contribution](https://github.com/NHSDigital/personal-demographics-service-api/blob/master/CONTRIBUTING.md) and the [community code of conduct](https://github.com/NHSDigital/personal-demographics-service-api/blob/master/CODE_OF_CONDUCT.md).

### Licensing
This code is dual licensed under the MIT license and the OGL (Open Government License). Any new work added to this repository must conform to the conditions of these licenses. In particular this means that this project may not depend on GPL-licensed or AGPL-licensed libraries, as these would violate the terms of those libraries' licenses.

The contents of this repository are protected by Crown Copyright (C).

## Development

### Requirements
* make
* nodejs + npm/yarn
* [poetry](https://github.com/python-poetry/poetry)

### Install
```
$ make install
```

#### Updating hooks
You can install some pre-commit hooks to ensure you can't commit invalid spec changes by accident. These are also run
in CI, but it's useful to run them locally too.

```
$ make install-hooks
```

### Make commands
There are `make` commands that alias some of this functionality:
 * `test` -- Lints the definition
 * `publish` -- Outputs the specification as a **single file** into the `dist/` directory
 * `serve` -- Serves a preview of the specification in human-readable format
 * `generate-examples` -- generate example objects from the specification
 * `validate` -- validate generated examples against FHIR R4


### VS Code Plugins

 * [openapi-lint](https://marketplace.visualstudio.com/items?itemName=mermade.openapi-lint) resolves links and validates entire spec with the 'OpenAPI Resolve and Validate' command
 * [OpenAPI (Swagger) Editor](https://marketplace.visualstudio.com/items?itemName=42Crunch.vscode-openapi) provides sidebar navigation


### Emacs Plugins

 * [**openapi-yaml-mode**](https://github.com/esc-emacs/openapi-yaml-mode) provides syntax highlighting, completion, and path help

### Speccy

> [Speccy](http://speccy.io/) *A handy toolkit for OpenAPI, with a linter to enforce quality rules, documentation rendering, and resolution.*

Speccy does the lifting for the following npm scripts:

 * `test` -- Lints the definition
 * `publish` -- Outputs the specification as a **single file** into the `dist/` directory
 * `serve` -- Serves a preview of the specification in human-readable format

(Workflow detailed in a [post](https://developerjack.com/blog/2018/maintaining-large-design-first-api-specs/) on the *developerjack* blog.)

:bulb: The `publish` command is useful when uploading to Apigee which requires the spec as a single file.

### Caveats

#### Swagger UI
Swagger UI unfortunately doesn't correctly render `$ref`s in examples, so use `speccy serve` instead.

#### Apigee Portal
The Apigee portal will not automatically pull examples from schemas, you must specify them manually.

### Postman Collection

`Patient Demographics Sandbox.postman_collection` must be kept in sync with the OAS and Sandbox manually.

Procedure:
 * Import the collection into Postman
 * Update requests and export the collection back into the repo
 * Re-generate the [Run in Postman button](https://learning.getpostman.com/docs/postman-for-publishers/run-in-postman/creating-run-button/) Markdown button link and update the OAS

## Deployment
:bulb: Consider using [direnv](https://direnv.net/) to manage your environment variables during development.

### Specification
Update the API Specification and derived documentation in the Portal.

`make deploy-spec` with environment variables:

* `APIGEE_USERNAME`
* `APIGEE_PASSWORD`
* `APIGEE_SPEC_ID`
* `APIGEE_PORTAL_API_ID`

### API Proxy & Sandbox Service
Redeploy the API Proxy and hosted Sandbox service.

`make deploy-proxy` with environment variables:

* `APIGEE_USERNAME`
* `APIGEE_PASSWORD`
* `APIGEE_ORGANIZATION`
* `APIGEE_ENVIRONMENTS`
* `APIGEE_APIPROXY`

#### Platform setup

Successful deployment of the API Proxy requires:

 1. A *Target Server* named `ig3`
