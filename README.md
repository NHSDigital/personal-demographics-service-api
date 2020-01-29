# personal-demographics-service-api
The specification for a RESTful HL7® FHIR® API to the *Personal Demographics Service*.

* `specification/` [Open API Specification](https://swagger.io/docs/specification/about/) describing the endpoints, methods, and messages exchanged by the API. Used to generate interactive documentation; the contract between the API and its consumers.
* `sandbox/` A NodeJS application implementing a mock implementation of the service. Used as a back-end service to the interactive documentation to illustrate interactions and concepts. Not intended to provide an exhaustive/faithful environment suitable for full development and testing.
* `scripts/` Utilities helpful to developers of this specification.

Documentation for application developers – consumers of the API this project describes – can be found on the [NHS Digital Developer Hub](https://emea-demo8-nhsdportal.apigee.io/).

## Contributing
Contributions to this project are welcome from anyone, providing they conform to the [guidelines for contribution](https://github.com/NHSDigital/personal-demographics-service-api/blob/master/CONTRIBUTING.md) and [community code of conduct](https://github.com/NHSDigital/personal-demographics-service-api/blob/master/CODE_OF_CONDUCT.md).

### Licensing
This code is dual licensed under the MIT license and the OGL (Open Government License). Any new work added to this repository must conform to the conditions of these licenses. In particular this means that this project may not depend on GPL- or AGPL-licensed libraries, as these would violated the terms of those libraries' licenses.

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
There are some pre-commit hooks you can install to ensure you can't commit invalid spec changes by accident. These are run
in CI as well, but it's useful to run them locally too.
```
$ make install-hooks
```

### Make commands
There's some make commands that alias some of the below functionality:
 * `test` -- Lints the definition
 * `publish` -- Outputs the specification as a **single file** into the `publish/` directory
 * `serve` -- Serves a preview of the specification in human-readable format
 * `release` -- copy the latest file from `publish/` to `public/`
 * `generate-examples` -- generate example objects from the specification
 * `validate` -- validate generated examples against FHIR R4


### VS Code Plugins

 * **openapi-lint** will resolve links and validate an entire specs with the 'OpenAPI Resolve and Validate' command
 * **OpenAPI (Swagger) Editor** provides sidebar navigation


### Emacs Plugins

 * [**openapi-yaml-mode**](https://github.com/esc-emacs/openapi-yaml-mode) provides syntax highlighting, completion, and path help

### Speccy

> [Speccy](http://speccy.io/) *A handy toolkit for OpenAPI, with a linter to enforce quality rules, documentation rendering, and resolution.*

Speccy does the lifting for the following npm scripts:

 * `test` -- Lints the definition
 * `publish` -- Outputs the specification as a **single file** into the `publish/` directory
 * `serve` -- Serves a preview of the specification in human-readable format
 * `release` -- copy the latest file from `publish/` to `public/`

(Workflow detailed in a [post](https://developerjack.com/blog/2018/maintaining-large-design-first-api-specs/) on the *developerjack* blog.)

:bulb: `publish` command is useful when uploading to Apigee which requires the spec as a single file. (There may be a way to provide a multi-file spec, update this doc if you find out.)

### Caveats

#### Swagger UI
The swagger ui unfortunately doesn't render `$ref`s in examples correctly, so using `speccy serve` is recommended instead.

#### Apigee Portal
The Apigee portal will not automatically pull examples from schemas, so they must be specified manually.

### Postman Collection

`Patient Demographics Sandbox.postman_collection` must be kept in sync with the OAS and Sandbox manually.

Procedure:
 * Import the collection into Postman
 * Update requests and export the collection back into the repo
 * Re-generate the [Run in Postman button](https://learning.getpostman.com/docs/postman-for-publishers/run-in-postman/creating-run-button/) Markdown button link and update the OAS
