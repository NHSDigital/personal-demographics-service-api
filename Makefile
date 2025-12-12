SHELL=/bin/bash -euo pipefail

install: install-node install-python install-fhir-validator install-hooks

install-python:
	poetry install

install-node:
	npm install
	npm install nvm

install-hooks:
	cp scripts/pre-commit .git/hooks/pre-commit

BIN_DIR := bin
# Java 11–compatible validator
FHIR_VALIDATOR := $(BIN_DIR)/org.hl7.fhir.validator.jar
FHIR_VALIDATOR_URL := https://github.com/hapifhir/org.hl7.fhir.core/releases/download/6.7.9/org.hl7.fhir.validator.jar

karate:
	cd karate-tests && mvn clean test -Dtest=TestParallel

lint:
	npm run lint-oas
	npm run lint-karate-js
	find . -name '*.py' | xargs poetry run flake8
	find . -name '*.sh' | grep -v node_modules | xargs shellcheck

install-fhir-validator:
	@mkdir -p $(BIN_DIR)
	@if [ ! -s "$(FHIR_VALIDATOR)" ]; then \
		echo "Downloading FHIR validator: $(FHIR_VALIDATOR_URL)"; \
		curl -fSL "$(FHIR_VALIDATOR_URL)" -o "$(FHIR_VALIDATOR)"; \
	fi
	@test -s "$(FHIR_VALIDATOR)" || (echo "Validator jar missing or empty"; exit 1)

validate: install-fhir-validator
	@echo "Validating examples..."
	java -jar "$(FHIR_VALIDATOR)" build/examples/**/*application_fhir+json*.json -version 4.0.1 -tx n/a -extension any | tee /tmp/validation.txt

prism: publish
	prism proxy build/personal-demographics.json ${OAUTH_BASE_URI}/${PDS_BASE_PATH} --errors --validate-request false

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
	cd karate-tests && docker build -t nhs/pds-sandbox . && docker run --rm --name karate-sandbox -p 9000:9000 nhs/pds-sandbox

build-proxy:
	scripts/build_proxy.sh

release: clean publish build-proxy
	mkdir -p dist
	cp -R build/. dist/
	cp -R terraform dist
	cp -R tests dist
	cp -R karate-tests dist
	cp -R postman dist

	cp ecs-proxies-deploy.yml dist/ecs-deploy-sandbox.yml
	cp ecs-proxies-deploy.yml dist/ecs-deploy-internal-qa-sandbox.yml
	cp ecs-proxies-deploy.yml dist/ecs-deploy-internal-dev-sandbox.yml

	cp pyproject.toml dist/pyproject.toml

test-custom-attribute-reporter:
	poetry run pytest scripts/custom_attribute_reporter/

test-local-sandbox:
	cd karate-tests && mvn clean test -Dtest=TestLocalMockParallel

test-sandbox:
	cd karate-tests && mvn clean test -Dtest=TestMockParallel

validate-xml:
	poetry run python scripts/xml_validator.py

scan-secrets:
	# Please do not change this `check=whole-history` setting, as new patterns may be added or history may be rewritten.
	check=whole-history ./scripts/githooks/scan-secrets.sh
