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

Redeploy the API Proxy. See the main [README.md](../README.md).

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
