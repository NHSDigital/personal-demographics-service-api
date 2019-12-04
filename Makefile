install: install-node install-python install-fhire-validator

install-python:
	pipenv install

install-node:
	npm install

install-fhir-validator:
	mkdir -p bin
	test -f bin/org.hl7.fhir.validator.jar || curl https://fhir.github.io/latest-ig-publisher/org.hl7.fhir.validator.jar > bin/org.hl7.fhir.validator.jar

test:
	npm run test

publish:
	npm run publish

serve:
	npm run serve

develop: serve

generate-examples: publish
	mkdir -p dist/examples
	pipenv run python scripts/generate_examples.py < dist/patient-information-api.json > dist/examples/Patient.json
