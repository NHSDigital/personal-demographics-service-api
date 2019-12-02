test:
	npm run test

publish:
	npm run publish

serve:
	npm run serve

develop: serve

release: publish
	npm run release
