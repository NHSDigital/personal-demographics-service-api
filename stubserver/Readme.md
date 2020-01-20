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

To deploy you need to set enviroment variables for Apigee. Your credentials will not work if multi-factor authentication is setup on your account.

You need to set:
- Username
- Password
- Apigee Spec ID
- Apigee Portal API ID

To set environment varaibles:

```
export APIGEE_USER=<USERNAME>
export APIGEE_PASS=<PASSWORD>
export APIGEE_SPEC_ID=<SPEC ID>
export APIGEE_PORTAL_API_ID=<PORTAL_API)ID>
```

Then to deploy:

```
npm run deploy
```

Will collect all the assets in the `dist/` folder and create a new **undeployed** revision of the *Patient-Information* API Proxy.

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
