install: install-node install-python install-fhir-validator

install-python:
	poetry install

install-node:
	npm install

install-fhir-validator:
	mkdir -p bin
	test -f bin/org.hl7.fhir.validator.jar || curl https://fhir.github.io/latest-ig-publisher/org.hl7.fhir.validator.jar > bin/org.hl7.fhir.validator.jar

test:
	npm run test

validate: generate-examples
	java -jar bin/org.hl7.fhir.validator.jar dist/examples/Patient.json -version 4.0.1 | tee /tmp/validation.txt

publish:
	npm run publish

serve: generate-examples
	npm run serve

generate-examples: publish
	mkdir -p dist/examples
	poetry run python scripts/generate_examples.py < dist/patient-information-api.json > dist/examples/Patient.json
