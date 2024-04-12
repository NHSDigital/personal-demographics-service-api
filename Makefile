SHELL=/bin/bash -euo pipefail

install: install-node install-python install-fhir-validator install-hooks

install-python:
	poetry install

install-node:
	npm install
	npm install nvm
	cd sandbox && npm install

install-hooks:
	cp scripts/pre-commit .git/hooks/pre-commit

install-fhir-validator:
	mkdir -p bin
	test -f bin/org.hl7.fhir.validator.jar || curl -L https://github.com/hapifhir/org.hl7.fhir.core/releases/latest/download/validator_cli.jar > bin/org.hl7.fhir.validator.jar

karate:
	cd karate-tests && mvn clean test

karate-sandbox:
	cd karate-tests && bash build-sandbox-ado.sh && docker run -d --name karate-sandbox nhs/pds-sandbox:latest

lint:
	npm run lint-oas
	npm run lint-karate-js
	npm run lint-node-sandbox
	find . -name '*.py' | xargs poetry run flake8
	find . -name '*.sh' | grep -v node_modules | xargs shellcheck

validate: generate-examples
	java -jar bin/org.hl7.fhir.validator.jar build/examples/**/*application_fhir+json*.json -version 4.0.1 -tx n/a -extension any | tee /tmp/validation.txt

publish: clean
	mkdir -p build
	npm run publish 2> /dev/null

publish-short-version:
	swagger-cli bundle specification/personal-demographics.yaml -o short-version/personal-demographics-short-version.json

publish-merged-version: clean publish publish-short-version

serve: update-examples
	npm run serve

clean:
	rm -rf build
	rm -rf dist
	rm -rf short-version

generate-examples: clean publish
	mkdir -p build/examples
	poetry run python scripts/generate_examples.py build/personal-demographics.json build/examples
	scripts/duplicate_examples.sh

update-examples: generate-examples
	scripts/update_examples.sh
	make publish

check-licenses:
	npm run check-licenses
	scripts/check_python_licenses.sh

deploy-proxy: update-examples
	scripts/deploy_proxy.sh

deploy-spec: update-examples
	scripts/deploy_spec.sh

format:
	poetry run black **/*.py

sandbox: update-examples
	cd sandbox && npm run start

build-proxy:
	scripts/build_proxy.sh

release: clean publish build-proxy
	mkdir -p dist
	cp -R build/. dist/
	cp -R terraform dist
	cp -R tests dist
	cp /tmp/karate/karate-core/target/karate-core-1.6.0-SNAPSHOT-shaded.jar karate-tests/karate.jar
	cp -R karate-tests dist

	cp ecs-proxies-deploy.yml dist/ecs-deploy-sandbox.yml
	cp ecs-proxies-deploy.yml dist/ecs-deploy-internal-qa-sandbox.yml
	cp ecs-proxies-deploy.yml dist/ecs-deploy-internal-dev-sandbox.yml

	cp pyproject.toml dist/pyproject.toml

test-sandbox: export APIGEE_ENVIRONMENT = local
test-sandbox: export PDS_BASE_PATH = local
test-sandbox:
	poetry run pytest -v tests/sandbox/test_sandbox.py

validate-xml:
	poetry run python scripts/xml_validator.py
