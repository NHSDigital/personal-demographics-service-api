# apim-definitions
Temporary repository of API definitions for the API management project.

## APIs
* Patient Information API

## Development

WIP: Still working on finding a great set of tools for working with these files. Please contribute!

### VS Code Plugins

 * **openapi-lint** will resolve links and validate an entire specs with the 'OpenAPI Resolve and Validate' command
 * **OpenAPI (Swagger) Editor** provides sidebar navigation
 

### Emacs Plugins

 * [**openapi-yaml-mode**](https://github.com/esc-emacs/openapi-yaml-mode) provides syntax highlighting, completion, and path help

### Swagger UI in Docker

Using relative paths in definition references means [editor.swagger.io](http://editor.swagger.io/) won't work.

An easy way to visualise the API during development is using Swagger UI in Docker. Run the following command in a shell from within the repo root to view the Patient Information API spec at http://localhost/.

Mounting the `components/` sudirectory into `/usr/share/nginx/html/components` is necessary to serve the referenced definitions. Further mounts may be necessary in the future. See this [GitHub Issue](https://github.com/swagger-api/swagger-ui/issues/4915) for context.

```
docker run -p 80:8080 \
    -e SWAGGER_JSON=/spec/patient-information-api.yaml \
    -v ${pwd}:/spec \
    -v ${pwd}\components\:/usr/share/nginx/html/components \
    swaggerapi/swagger-ui
```

Speccy's `serve` subcommand provides similar functionality (see below) but requires you restart the service before changes are reflected.

### Speccy

> [Speccy](http://speccy.io/) *A handy toolkit for OpenAPI, with a linter to enforce quality rules, documentation rendering, and resolution.*

Speccy does the lifting for the following npm scripts:

 * `test` -- Lints the definition
 * `publish` -- Outputs the specification as a **single file** into the `publish/` directory
 * `serve` -- Serves a preview of the specification in human-readable format
 * `release` -- copy the latest file from `publish/` to `public/`

(Workflow detailed in a [post](https://developerjack.com/blog/2018/maintaining-large-design-first-api-specs/) on the *developerjack* blog.)

:bulb: `publish` command is useful when uploading to Apigee which requires the spec as a single file. (There may be a way to provide a multi-file spec, update this doc if you find out.)
