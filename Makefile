SHELL=/bin/bash -euo pipefail

install: install-node install-python install-fhir-validator install-hooks

install-python:
	poetry install

install-node:
	npm install --dev
	cd sandbox && npm install

install-hooks:
	cp scripts/pre-commit .git/hooks/pre-commit

install-fhir-validator:
	mkdir -p bin
	test -f bin/org.hl7.fhir.validator.jar || curl https://fhir.github.io/latest-ig-publisher/org.hl7.fhir.validator.jar > bin/org.hl7.fhir.validator.jar

test:
	npm run test

validate: generate-examples
	java -jar bin/org.hl7.fhir.validator.jar dist/examples/**/*application_fhir+json*.json -version 4.0.1 -tx n/a | tee /tmp/validation.txt

publish:
	npm run publish 2> /dev/null

serve: update-examples
	npm run serve

clean:
	rm -rf dist/examples

generate-examples: publish clean
	mkdir -p dist/examples
	poetry run python scripts/generate_examples.py dist/patient-demographics-service-api.json dist/examples

update-examples: generate-examples
	jq -rM . <dist/examples/resources/Patient.json >specification/components/examples/Patient.json
	make publish

check-licenses:
	npm run check-licenses
	scripts/check_python_licenses.sh

deploy-proxy:
	mkdir -p dist
	rm -rf dist/apiproxy
	cp -R apiproxy/ dist/
	mkdir -p dist/apiproxy/resources/hosted/mocks
	cp stubserver/*.js stubserver/*.json stubserver/*.yaml dist/apiproxy/resources/hosted/
	cp -L stubserver/mocks/*.json dist/apiproxy/resources/hosted/mocks/
	node_modules/.bin/apigeetool deployproxy --environments "test,prod" --api apm-312 --directory dist/ --verbose
