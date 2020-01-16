# Stub API Server

Stub API Server built using [hapi](https://hapi.dev/) framework deployable as a [Apigee Hosted Target](https://docs.apigee.com/api-platform/hosted-targets/hosted-targets-overview).

Intended for "sandbox" functionality, and is the target endpoint for the hosted docs' *Try it now* functionality.

## Developing

```
npm install
npm run serve
```

 * Use the examples from the OAS (`components/examples/`) sym-linking them into the app.

## Deployment

Set $APIGEE_USER
Set $APIGEE_PASS

```
npm run deploy
```

Will collect all the assets in the `dist/` folder and create a new **undeployed** revision of the *Patient-Information* API Proxy.

Requires a username and password.

Uses [apigeetool](https://www.npmjs.com/package/apigeetool).

## Endpoints

- [ ] GET    `/Patient`
- [x] GET    `/Patient/{nhs_number}`
- [ ] PATCH  `/Patient/{nhs_number}`
- [ ] GET    `/Patient/{nhs_number}/RelatedPerson`
- [ ] POST   `/Patient/{nhs_number}/RelatedPerson`
- [ ] GET    `/Patient/{nhs_number}/RelatedPerson/{id}`
- [ ] PUT    `/Patient/{nhs_number}/RelatedPerson/{id}`
- [ ] DELETE `/Patient/{nhs_number}/RelatedPerson/{id}`
- [ ] GET    `/Patient/{nhs_number}/ReasonableAdjustment`
- [ ] POST   `/Patient/{nhs_number}/ReasonableAdjustment`
- [ ] GET    `/Patient/{nhs_number}/ReasonableAdjustment/{id}`
- [ ] PUT    `/Patient/{nhs_number}/ReasonableAdjustment/{id}`
- [ ] DELETE `/Patient/{nhs_number}/ReasonableAdjustment/{id}`
- [ ] GET    `/Patient/{nhs_number}/Address`
- [ ] POST   `/Patient/{nhs_number}/Address`
- [ ] GET    `/Patient/{nhs_number}/Address/{id}`
- [ ] PUT    `/Patient/{nhs_number}/Address/{id}`
- [ ] DELETE `/Patient/{nhs_number}/Address/{id}`
