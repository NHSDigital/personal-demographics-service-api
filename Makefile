develop:
	docker run -p 8080:8080 -e SWAGGER_JSON=/spec/patient-information-api.yaml -v ${shell pwd}:/spec -v ${shell pwd}/components/:/usr/share/nginx/html/components swaggerapi/swagger-ui

test:
	npm run test

publish:
	npm run publish

serve:
	npm run serve

release: publish
	npm run release
