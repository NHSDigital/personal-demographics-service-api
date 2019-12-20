SHELL=/bin/bash -euo pipefail

install: install-node install-python install-fhir-validator install-hooks

install-python:
	poetry install

install-node:
	npm install

install-hooks:
	cp scripts/pre-commit .git/hooks/pre-commit

install-fhir-validator:
	mkdir -p bin
	test -f bin/org.hl7.fhir.validator.jar || curl https://fhir.github.io/latest-ig-publisher/org.hl7.fhir.validator.jar > bin/org.hl7.fhir.validator.jar

test:
	npm run test

validate: generate-examples
	java -jar bin/org.hl7.fhir.validator.jar dist/examples/**/* -version 4.0.1 -ig https://nhsconnect.github.io/FHIR-R4-Core-IG-Prototype | tee /tmp/validation.txt

publish:
	npm run publish 2> /dev/null

serve: generate-examples
	npm run serve

clean:
	rm -rf dist/examples

generate-examples: publish clean
	mkdir -p dist/examples
	poetry run python scripts/generate_examples.py dist/patient-information-api.json dist/examples
