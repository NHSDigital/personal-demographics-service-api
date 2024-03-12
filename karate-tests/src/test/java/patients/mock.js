context.read('classpath:helpers/nhs-number-validator.js');

session.sampleNhsNumbers = [
    "9494743881", "9996293491", "9991101934", "9994506749", "9990802718",
    "9998167892", "9991255192", "9991237127", "9993984140", "9995638231",
    "9992684526", "9996704394", "9994533630", "9991597581", "9993428043",
    "9995809699", "9990870632", "9991959823", "9995349000", "9994826220"
];

session.sampleNumberIndex = session.sampleNumberIndex || 0;

session.patients = session.patients || {
    '9000000009': context.read('classpath:stubs/patient/sandbox-patient.json'),
    '9000000025': context.read('classpath:stubs/oldSandbox/sensitive-patient.json'),
    '9693632109': context.read('classpath:stubs/patient/patient_9693632109.json')
}

session.periodSchema = context.read('classpath:schemas/Period.json')
session.addressSchema = context.read('classpath:schemas/Address.json')
session.humanNameSchema = context.read('classpath:schemas/HumanName.json')
session.contactPointSchema = context.read('classpath:schemas/ContactPoint.json')
session.generalPractitionerSchema = context.read('classpath:schemas/GeneralPractitionerReference.json')
session.schema = context.read('classpath:schemas/PatientNhsNumberAllocation.json')


if (request.pathMatches('/Patient/{nhsNumber}') && request.get) {
    response.headers = {
        'x-request-id': request.header('x-request-id'),
        'x-correlation-id': request.header('x-correlation-id')
    };
    let nhsNumber = request.pathParams.nhsNumber;
    var valid = validate(nhsNumber)
    if (!valid) {
        response.body = context.read('classpath:stubs/oldSandbox/errors/INVALID_RESOURCE_ID.json');
        response.status = 400
    } else {
        if (typeof session.patients[nhsNumber] == 'undefined') {
            response.body = context.read('classpath:stubs/oldSandbox/errors/RESOURCE_NOT_FOUND.json');
            response.status = 404
        } else {
            patient = session.patients[nhsNumber]
            response.body = patient;
            response.status = 200;
        }    
    }
}