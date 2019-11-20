# apim-definitions
Temporary repository of API definitions for the API management project.

## APIs
* Patient Information API

## Development

WIP: Still working on finding a great set of tools for working with these files. Please contribute!

### VS Code Plugins

 * **openapi-lint** will resolve links and validate an entire specs with the 'OpenAPI Resolve and Validate' command
 * **OpenAPI (Swagger) Editor** provides sidebar navigation

### Swagger UI in Docker

Using relative paths in definition references means [editor.swagger.io](http://editor.swagger.io/) won't work.

An easy way to visualise the API during development is using Swagger UI in Docker. Run the following command in PowerShell from within the repo root to view the Patient Information API spec at http://localhost/.

Mounting the `components/` sudirectory into `/usr/share/nginx/html/components` is necessary to serve the referenced definitions. Further mounts may be necessary in the future. See this [GitHub Issue](https://github.com/swagger-api/swagger-ui/issues/4915) for context.

```
docker run -p 80:8080 \
    -e SWAGGER_JSON=/spec/patient-information-api.yaml \
    -v ${pwd}:/spec \
    -v ${pwd}\components\:/usr/share/nginx/html/components \
    swaggerapi/swagger-ui
```
