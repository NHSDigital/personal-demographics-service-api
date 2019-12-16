# apim-definitions
Temporary repository of API definitions for the API management project.

## APIs
* Patient Information API

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
