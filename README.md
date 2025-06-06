# personal-demographics-service-api

![Build](https://github.com/NHSDigital/personal-demographics-service-api/workflows/Build/badge.svg?branch=master)

This is a RESTful HL7® FHIR® API for the *Personal Demographics Service*.

It includes:
* `karate-tests/` - our functional e2e API tests implemented using the Karate framework. [There is a separate readme for these tests at the moment](karate-tests/README.md)
* `specification/` - an [Open API Specification](https://swagger.io/docs/specification/about/) describing the endpoints, methods and messages exchanged by the API. Use it to generate interactive documentation; the contract between the API and its consumers.
* `sandbox/` - a Karate API mock application. Use it as a back-end service to the interactive documentation to illustrate interactions and concepts. It is not intended to provide an exhaustive/faithful environment suitable for full development and testing.
* `scripts/` - utilities helpful to developers of this specification.
* `apiproxy/` - the API proxy, which is deployed to our API platform hosted on Google Apigee Edge

Consumers of the API will find developer documentation on the [NHS Digital Developer Hub](https://digital.nhs.uk/developer/api-catalogue/personal-demographics-service-fhir).

This repo does *not* include the PDS FHIR API back-end. That is part of 'Core Spine' which is not currently open source.

## Contributing
Contributions to this project are welcome from anyone, providing that they conform to the [guidelines for contribution](https://github.com/NHSDigital/personal-demographics-service-api/blob/master/CONTRIBUTING.md) and the [community code of conduct](https://github.com/NHSDigital/personal-demographics-service-api/blob/master/CODE_OF_CONDUCT.md).

### Licensing
This code is dual licensed under the MIT license and the OGL (Open Government License). Any new work added to this repository must conform to the conditions of these licenses. In particular this means that this project may not depend on GPL-licensed or AGPL-licensed libraries, as these would violate the terms of those libraries' licenses.

The contents of this repository are protected by Crown Copyright (C).

## Setup

N.B. that some functionality requires environment variables to be set. Some of these are described lower down in the readme, whilst others can be found in [the environment variables section of this confluence page](https://nhsd-confluence.digital.nhs.uk/display/SPINE/Personal+Demographics+Service+api+setup)


Windows users should install [Windows Subsystem for Linux (WSL)](https://learn.microsoft.com/en-us/windows/wsl/install). Any distro is fine, though ubuntu/debian are recommended.

## Installing requirements
Install build requirements. This will make sure you don't hit any weird python issues later.
```bash
sudo apt update
sudo apt install make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev git net-tools python-openssl
```
If you get the error "Unable to locate package python-openssl", try
```bash
sudo apt install python3-openssl
```

Install [pyenv](https://github.com/pyenv/pyenv) using the code below and then follow their [guide](https://github.com/pyenv/pyenv#set-up-your-shell-environment-for-pyenv) to integrate it with your terminal
```bash
curl https://pyenv.run | bash
exec $SHELL
```
If the command isn't working you can also [try the instructions here.](https://www.liquidweb.com/kb/how-to-install-pyenv-on-ubuntu-18-04/)

Install python 3.9
```bash
pyenv install 3.9
```
Either set this as your global python (if this is not incompatible with your other projects),
```bash
pyenv global 3.9
```
or local to repository, if there is not a python-version file installed (you might have to raise a PR to add the file that's created).
```bash
pyenv local 3.9
python --version
```

Install poetry, then run 'poetry install' to install dependencies. Makes sure you change directory to this repo.
```bash
curl -sSL https://install.python-poetry.org | python3
poetry install
```

Install nvm & npn
```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.35.2/install.sh | bash
# Close and reopen your terminal window, or use 'exec $SHELL'
nvm install lts/iron
nvm use lts/iron
npm --version
```

Install Java
```bash
sudo apt install default-jre default-jdk
java -version
```

Install pytest
```bash
pip install -U pytest
sudo apt-get update
sudo apt-get install jq
```

Install shellcheck (we use this for linting .sh files)
```bash
sudo apt install shellcheck
```

Install gitleaks (we use this for scanning for secrets)
* Extract gitleaks tarball to /usr/local/bin
```bash
cd ~/Downloads
curl -LO https://github.com/gitleaks/gitleaks/releases/download/v8.27.0/gitleaks_8.27.0_linux_x64.tar.gz
sudo tar -xvzf gitleaks_8.27.0_linux_x64.tar.gz -C /usr/local/bin gitleaks
```
* Ensure that /usr/local/bin is part of your $PATH environment variable
```bash
echo $PATH
```
* If it does not exist in the output, then add the following line to .bashrc file
```bash
export PATH="/usr/local/bin:$PATH"
```
* You may need to open a new terminal/vscode for these changes to take affect

Next open powershell and get the wsl ip (make sure wsl is running)
The purpose of the following instructions is to enable you to use postman if you wish against the sandbox.
```bash
wsl hostname -i
```
Add a proxy and open the windows fire wall, replace [PORT] with the port you want to connect to.
connected address is the ip wsl is operating on (from `wsl hostname -i`)
```bash
netsh interface portproxy add v4tov4 listenport=9000 listenaddress=0.0.0.0 connectport=[PORT] connectaddress=127.0.1.1
# Check it's been added
netsh interface portproxy show v4tov4
firewall -add port 9000 
```

## Development


#### Updating hooks
You can install some pre-commit hooks to ensure you can't commit invalid spec changes by accident. These are also run
in CI, but it's useful to run them locally too.

```bash
make install-hooks
```

### Environment Variables
Various scripts and commands rely on environment variables being set. These are documented with the commands.

:bulb: Consider using [direnv](https://direnv.net/) to manage your environment variables during development and maintaining your own `.envrc` file - the values of these variables will be specific to you and/or sensitive.

### Make commands
There are `make` commands that alias some of this functionality:
 * `lint` -- Lints the spec and code
 * `publish` -- Outputs the specification as a **single file** into the `dist/` directory
 * `serve` -- Serves a preview of the specification in human-readable format
 * `generate-examples` -- generate example objects from the specification
 * `validate` -- validate generated examples against FHIR R4

### Running tests
#### Sandbox Tests

Run the install command if not ran already
```bash
make install
```

To run the tests against a local version of the sandbox, use:
```bash
make test-local-sandbox
```

To run the tests against the production sandbox, us:
```bash
make test-sandbox
```

#### Jest

A short javascript file, RestrictRequests.js, handles restricting patient-access requests. Jest is use to unit test this file. To run these tests locally,
```
npm run jest
```


### VS Code Plugins

 * [openapi-lint](https://marketplace.visualstudio.com/items?itemName=mermade.openapi-lint) resolves links and validates entire spec with the 'OpenAPI Resolve and Validate' command
 * [OpenAPI (Swagger) Editor](https://marketplace.visualstudio.com/items?itemName=42Crunch.vscode-openapi) provides sidebar navigation
 * [ESLint](https://marketplace.visualstudio.com/items?itemName=dbaeumer.vscode-eslint) useful helper when you're working with JavaScript files

### Emacs Plugins

 * [**openapi-yaml-mode**](https://github.com/esc-emacs/openapi-yaml-mode) provides syntax highlighting, completion, and path help

### Redocly

> [Redocly](https://redocly.com/) *Beautiful API documentation loved by teams and API consumers. Brought to you by the open-source extraordinaires behind Redoc*

Redocly does the lifting for the following npm scripts:

 * `lint` -- Lints the definition
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
 * Log in to the Postman account
 * Update requests
 * Export the collection back into the repo

 The link in `personal-demographics.yaml` will get the most recent version of the collection.

## Deployment

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
* `APIGEE_ENVIRONMENTS` - Comma-separated list of environments to deploy to (e.g. `test,prod`)
* `APIGEE_APIPROXY` - Name of the API Proxy for deployment
* `APIGEE_BASE_PATH` - The proxy's base path (must be unique)

:bulb: Specify your own API Proxy (with base path) for use during development.

#### Platform setup

Successful deployment of the API Proxy requires:

 1. *Target Servers*:
    1. `spine-demographics`: Gateway to PDS API
    2. `spine-demographics-int` Gateway to PDS INT API (Only avaliable for pull requests)
    3. `identity-server` - Identity Provider's OAuth server
 2. An **encrypted** (for production) *Key-Value Map* named `pds-variables-encrypted`, containing:
    1. Key: `NHSD-ASID`, Value: Accredited System ID (ASID) identifying the API Gateway
 3. A *Key-Value Map* named `pds-variables`, containing:
    1. Key: `jwks_path`, Value: Path on `identity-server` Target Server to JSON Web Key Set (JWKS)

:bulb: For Sandbox-running environments (`test`) these need to be present for successful deployment but can be set to empty/dummy values.
