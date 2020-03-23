SHELL=/bin/bash -euo pipefail

install: install-node install-python install-fhir-validator install-hooks

install-python:
	poetry install

install-node:
	npm install
	cd sandbox && npm install

install-hooks:
	cp scripts/pre-commit .git/hooks/pre-commit

install-fhir-validator:
	mkdir -p bin
	test -f bin/org.hl7.fhir.validator.jar || curl https://fhir.github.io/latest-ig-publisher/org.hl7.fhir.validator.jar > bin/org.hl7.fhir.validator.jar

test:
	npm run test

lint:
	npm run lint
	cd sandbox && npm run lint && cd ..
	poetry run flake8 **/*.py
	find -name '*.sh' | grep -v node_modules | xargs shellcheck

validate: generate-examples
	java -jar bin/org.hl7.fhir.validator.jar build/examples/**/*application_fhir+json*.json -version 4.0.1 -tx n/a | tee /tmp/validation.txt

publish: clean
	mkdir -p build
	npm run publish 2> /dev/null

serve: update-examples
	npm run serve

clean:
	rm -rf build
	rm -rf dist

generate-examples: publish clean
	mkdir -p build/examples
	poetry run python scripts/generate_examples.py build/personal-demographics.json build/examples
	cp build/examples/resources/Patient.json build/examples/resources/Patient-Jayne-Smyth.json
	cp build/examples/resources/Search_Patient.json build/examples/resources/Search_Patient-Jayne-Smyth.json
	sed -i -e 's/9000000009/9000000010/g; s/Jane/Jayne/g; s/Smith/Smyth/g;' build/examples/resources/Patient-Jayne-Smyth.json
	sed -i -e 's/9000000009/9000000010/g; s/Jane/Jayne/g; s/Smith/Smyth/g;' build/examples/resources/Search_Patient-Jayne-Smyth.json

update-examples: generate-examples
	jq -rM . <build/examples/resources/Patient.json >specification/components/examples/Patient.json
	jq -rM . <build/examples/resources/Patient-Jayne-Smyth.json >specification/components/examples/Patient-Jayne-Smyth.json
	jq -rM . <build/examples/resources/Search_Patient.json >specification/components/examples/Search_Patient.json
	jq -rM . <build/examples/resources/Search_Patient-Jayne-Smyth.json >specification/components/examples/Search_Patient-Jayne-Smyth.json
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
	tar -zcvf dist/package.tar.gz build

