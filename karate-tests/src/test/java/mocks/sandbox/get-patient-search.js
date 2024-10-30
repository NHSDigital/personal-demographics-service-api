/*
  Supporting functions for building responses
*/

/* Karate objects */
/* global context, request, response */

/* Functions defined in supporting-functions.js */
/* global validateHeaders, setAdditionalPropertiesError, setInvalidValueError, setInvalidSearchDataError, setMissingValueError, setUnsupportedServiceError, basicResponseHeaders, timestampBody */

/* Constants defined in stubs.js */
/* global EMPTY_SEARCHSET, SEARCH_PATIENT_9000000009, FUZZY_SEARCH_PATIENT_17, WILDCARD_SEARCH, RESTRICTED_PATIENT_SEARCH, SIMPLE_SEARCH */

const MOCK_SINGLE_SEARCHSET = context.read('classpath:mocks/stubs/searchResponses/mock_single_searchset.json')
const MOCK_MULTIPLE_SEARCHSET = context.read('classpath:mocks/stubs/searchResponses/mock_multiple_searchset.json')

/*
 * These stubs are used for our search tests
 */
const JACKIE_JONES_SEARCHSET = context.read('classpath:mocks/stubs/searchResponses/jackie_jones_searchset.json')
const RODNEY_GODSOE_SEARCHSET = context.read('classpath:mocks/stubs/searchResponses/rodney_godsoe_searchset.json')
const MARTHA_MASSAM_SEARCHSET = context.read('classpath:mocks/stubs/searchResponses/martha_massam_searchset.json')
const YOUDS_SEARCHSET = context.read('classpath:mocks/stubs/searchResponses/youds_searchset.json')
const JOE_BLOGS_HISTORIC_NAME_SEARCHSET = context.read('classpath:mocks/stubs/searchResponses/bill_garton_searchset.json')
const PAULINE_ATTISON_SEARCHSET = context.read('classpath:mocks/stubs/searchResponses/pauline_attison_searchset.json')
const JOHN_PAUL_SMITH_SEARCHSET = context.read('classpath:mocks/stubs/searchResponses/john_paul_smith_searchset.json')
const CUFF_SUPERSEDED_SEARCHSET = context.read('classpath:mocks/stubs/searchResponses/cuff_superseded_searchset.json')
const OTHER_GIVENNAME_SEARCHSET = context.read('classpath:mocks/stubs/searchResponses/other_givenName.json')
const MULTIMATCHWITHPHONEANDEMAIL_SEARCHSET = context.read('classpath:mocks/stubs/searchResponses/multimatch_phoneAndEmail_searchset.json')
const COUNTRYCODE_SEARCHSET = context.read('classpath:mocks/stubs/searchResponses/countrycode_mobile_searchset.json')
const HISTORIC_EMAIL_SEARCHSET = context.read('classpath:mocks/stubs/searchResponses/historic_email_searchset.json')
const POSTALCODE_WILDCARD_SEARCHSET = context.read('classpath:mocks/stubs/searchResponses/postalcode_wildcard_searchset.json')
const GP_SEARCHSET = context.read('classpath:mocks/stubs/searchResponses/general_practitioner_searchset.json')
const DEATHDATE_SEARCHSET = context.read('classpath:mocks/stubs/searchResponses/dateOfDeath_searchset.json')
const FUZZY_SINGLE_SEARCHSET = context.read('classpath:mocks/stubs/searchResponses/fuzzy_single_searchset.json')
const FUZZY_MULTI_SEARCHSET = context.read('classpath:mocks/stubs/searchResponses/fuzzy_multimatch_searchset.json')
const HISTORIC_DATA_SEARCHSET = context.read('classpath:mocks/stubs/searchResponses/med_rowenad_searchset.json')
const TOO_MANY_MATCHES = context.read('classpath:mocks/stubs/searchResponses/TOO_MANY_MATCHES.json')

function janeSmithSearchsetWithScore (score) {
  return {
    resourceType: 'Bundle',
    type: 'searchset',
    total: 1,
    entry: [
      {
        fullUrl: 'https://api.service.nhs.uk/personal-demographics/FHIR/R4/Patient/9000000009',
        search: { score },
        resource: SEARCH_PATIENT_9000000009
      }
    ]
  }
}

/*
    Specific query param validation to support main handler
*/
function validateQueryParams (request) {
  const VALID_PARAMS = [
    '_fuzzy-match', '_exact-match', '_history', '_max-results',
    'family', 'given', 'gender', 'birthdate', 'death-date', 'history',
    'address-postcode', 'address-postalcode', 'general-practitioner', 'email', 'phone'
  ]

  // check that params were actually provided
  if (Object.keys(request.params).length === 0) {
    return setUnsupportedServiceError()
  }

  // reject any invalid params
  const validParams = []
  const invalidParams = []
  for (const paramName in request.params) {
    if (VALID_PARAMS.includes(paramName)) {
      validParams.push(paramName)
    } else {
      invalidParams.push(paramName)
    }
  }
  if (invalidParams.length === 3) {
    // the diagnostics message isn't built dynamically, because the order of properties doesn't correspond to the order of the params
    // instead, this is a dumb rule that just assumes the three invalid params are the ones our test uses
    const diagnostics = "Invalid request with error - Additional properties are not allowed ('model', 'manufacturer', 'year' were unexpected)"
    return setAdditionalPropertiesError(diagnostics)
  }
  if (invalidParams.length === 1) {
    const diagnostics = `Invalid request with error - Additional properties are not allowed ('${invalidParams[0]}' was unexpected)`
    return setAdditionalPropertiesError(diagnostics)
  }

  // check the validity of any date params first
  const birthDateArray = request.params.birthdate
  if (birthDateArray) {
    for (const index in birthDateArray) {
      const birthDate = birthDateArray[index]
      if (!birthDate || !birthDate.match(/^(eq|ge|le)?[0-9]{4}-[0-9]{2}-[0-9]{2}$/)) {
        const diagnostics = `Invalid value - '${birthDate}' in field 'birthdate'`
        return setInvalidValueError(diagnostics)
      }
    }
  }
  const deathDateArray = request.params['death-date']
  if (deathDateArray) {
    for (const index in deathDateArray) {
      const deathDate = deathDateArray[index]
      if (!deathDate || !deathDate.match(/^(eq|ge|le)?[0-9]{4}-[0-9]{2}-[0-9]{2}$/)) {
        const diagnostics = `Invalid value - '${deathDate}' in field 'death-date'`
        return setInvalidValueError(diagnostics)
      }
    }
  }

  // check that the birthdate was provided
  if (!validParams.includes('birthdate')) {
    const diagnostics = "Missing value - 'birth_date/birth_date_range_start/birth_date_range_end'"
    return setMissingValueError(diagnostics)
  }
  // check that the family name was provided
  if (!validParams.includes('family')) {
    const diagnostics = "Invalid search data provided - 'No searches were performed as the search criteria did not meet the minimum requirements'"
    return setInvalidSearchDataError(diagnostics)
  }

  return true
}

function otherJaneSmithParamsAreValid (request) {
  const phone = request.param('phone')
  const email = request.param('email')
  return (!phone || phone === '01632960587') && (!email || email === 'jane.smith@example.com')
}

// Define match cases as functions
const matchCases = [
  {
    condition: (params) => params.fuzzyMatch && params.family === 'Blogs' && params.given[0] === 'Joe' && params.birthDate[0] === '1955-11-05',
    action: () => timestampBody(JOE_BLOGS_HISTORIC_NAME_SEARCHSET)
  },
  {
    condition: (params) => params.fuzzyMatch && params.family === 'ATTSÖN' && params.given[0] === 'PÀULINÉ' && params.birthDate[0] === '1960-07-14',
    action: () => timestampBody(PAULINE_ATTISON_SEARCHSET)
  },
  {
    condition: (params) => params.fuzzyMatch && params.phone === '01222111111' && params.email === 'test@test.com',
    action: () => timestampBody(FUZZY_SINGLE_SEARCHSET)
  },
  {
    condition: (params) => params.fuzzyMatch && params.family === 'Smythe' && (params.given[0]) === 'Mat' && (params.birthDate[0]) === 'ge2000-05-03' &&
     params.gender === 'male' &&
     params.postalCode === 'DN17 4AA' && params.email !== 'rubbish@work.com',
    action: () => timestampBody(FUZZY_MULTI_SEARCHSET)
  },
  {
    condition: (params) => params.fuzzyMatch && params.family === 'Smythe' && (params.given[0]) === 'Mat' && (params.birthDate[0]) === 'ge2000-05-03' &&
     params.gender === 'male' &&
     params.postalCode === 'DN17 4AA' && params.email === 'rubbish@work.com',
    action: () => timestampBody(EMPTY_SEARCHSET)
  },
  {
    condition: (params) => params.fuzzyMatch && ['MED', 'HUME'].includes(params.family) && (params.given[0]) === 'Casey' && (params.birthDate[0]) === '1999-09-09',
    action: () => timestampBody(HISTORIC_DATA_SEARCHSET)
  },
  {
    condition: (params) => params.fuzzyMatch && params.family === 'MED' && (params.given[0]) === 'Casey' && (params.birthDate[0]) === '2024-01-12',
    action: () => timestampBody(EMPTY_SEARCHSET)
  },
  {
    condition: (params) => params.fuzzyMatch && params.family === 'LEEKE' && (params.given[0]) === 'Horace' && (params.birthDate[0]) === '1956-05-02' &&
     params.postalCode === 'DN16',
    action: () => timestampBody(EMPTY_SEARCHSET)
  },
  {
    condition: (params) => params.fuzzyMatch && !params.phone && !params.email,
    action: () => timestampBody(FUZZY_SEARCH_PATIENT_17)
  },
  {
    condition: (params) => params.fuzzyMatch && params.phone === '01632960587' && !params.email,
    action: () => timestampBody(janeSmithSearchsetWithScore(0.9124))
  },
  {
    condition: (params) => params.fuzzyMatch && params.email === 'jane.smith@example.com' && !params.phone,
    action: () => timestampBody(janeSmithSearchsetWithScore(0.9124))
  },
  {
    condition: (params) => params.fuzzyMatch && params.phone === '01632960587' && params.email === 'jane.smith@example.com',
    action: () => timestampBody(janeSmithSearchsetWithScore(0.9542))
  },
  {
    condition: (params) => params.historyMatch && ['Smith', 'smith'].includes(params.family) && ['Male', 'male'].includes(params.gender) &&
    (params.birthDate[0]) === 'eq2000-05-05' && params.email === 'Historic@historic.com',
    action: () => timestampBody(HISTORIC_EMAIL_SEARCHSET)
  },
  {
    condition: (params) => params.historyMatch && ['HUME'].includes(params.family) && (params.birthDate[0]) === '1999-09-09',
    action: () => timestampBody(HISTORIC_DATA_SEARCHSET)
  },
  {
    condition: (params) => params.historyMatch && params.family === 'MED' && (params.birthDate[0]) === '2024-01-12',
    action: () => timestampBody(EMPTY_SEARCHSET)
  },
  {
    condition: (params) => ['Sm*', 'sm*'].includes(params.family) && !params.phone && !params.email && !params.maxResults,
    action: () => timestampBody(WILDCARD_SEARCH)
  },
  {
    condition: (params) => ['Sm*', 'sm*'].includes(params.family) && !params.phone && !params.email && parseInt(params.maxResults) < 2,
    action: () => TOO_MANY_MATCHES
  },
  {
    condition: (params) => ['Sm*', 'sm*'].includes(params.family) && params.phone === '01632960587' && params.email,
    action: () => timestampBody(janeSmithSearchsetWithScore(1))
  },
  {
    condition: (params) => ['Sm*', 'sm*'].includes(params.family) && params.email === 'jane.smith@example.com' && !params.phone,
    action: () => timestampBody(janeSmithSearchsetWithScore(1))
  },
  {
    condition: (params) => ['Sm*', 'sm*'].includes(params.family) && params.email === 'jane.smith@example.com' && params.phone === '01632960587',
    action: () => timestampBody(janeSmithSearchsetWithScore(1))
  },
  {
    condition: (params) => ['Sm*', 'sm*'].includes(params.family) && params.email === 'janet.smythe@example.com',
    action: () => timestampBody(janeSmithSearchsetWithScore(1))
  },
  {
    condition: (params) => ['Sm*', 'sm*'].includes(params.family) && params.email === 'test@test.com' && params.phone === '01234123123' &&
     (params.birthDate[0]) === 'eq2000-05-05',
    action: () => timestampBody(MULTIMATCHWITHPHONEANDEMAIL_SEARCHSET)
  },
  {
    condition: (params) => ['Smythe', 'smythe'].includes(params.family),
    action: () => timestampBody(RESTRICTED_PATIENT_SEARCH)
  },
  {
    condition: (params) => ['Smith', 'smith'].includes(params.family) && ['Female', 'female'].includes(params.gender) &&
    (params.birthDate[0] === 'eq2010-10-22' || (params.birthDate[0] === 'ge2010-10-21' && params.birthDate[1] === 'le2010-10-23')) &&
     otherJaneSmithParamsAreValid(request),
    action: () => timestampBody(SIMPLE_SEARCH)
  },
  {
    condition: (params) => ['Smith', 'smith'].includes(params.family) && ['Male', 'male'].includes(params.gender) && (params.given[0]) === 'John Paul' &&
     params.given[1] === 'James',
    action: () => timestampBody(JOHN_PAUL_SMITH_SEARCHSET)
  },
  {
    condition: (params) => ['CUFF', 'Cuff'].includes(params.family) && ['Female', 'female'].includes(params.gender) &&
     (params.birthDate[0] === 'eq1926-01-07'),
    action: () => timestampBody(CUFF_SUPERSEDED_SEARCHSET)
  },
  {
    condition: (params) => ['Smith', 'smith'].includes(params.family) && ['Male', 'male'].includes(params.gender) &&
     (params.birthDate[0]) === 'eq2000-05-05' &&
     (params.given[0]) === 'Sam' && (params.given[1]) === 'Bob',
    action: () => timestampBody(OTHER_GIVENNAME_SEARCHSET)
  },
  {
    condition: (params) => ['Smith', 'smith'].includes(params.family) && ['Male', 'male'].includes(params.gender) &&
     (params.birthDate[0]) === 'eq2000-05-05' &&
     params.phone === '01234123123' && params.email === 'test@test.com',
    action: () => timestampBody(MULTIMATCHWITHPHONEANDEMAIL_SEARCHSET)
  },
  {
    condition: (params) => ['Muir', 'Muir'].includes(params.family) && ['Male', 'male'].includes(params.gender) &&
     (params.birthDate[0]) === 'eq2017-09-06' &&
     params.phone === '00917855986859',
    action: () => timestampBody(COUNTRYCODE_SEARCHSET)
  },
  {
    condition: (params) => ['DN17*'].includes(params.postalCode) && ['Smith', 'smith'].includes(params.family) &&
     ['Male', 'male'].includes(params.gender) &&
     (params.birthDate[0]) === 'eq2000-05-05',
    action: () => timestampBody(POSTALCODE_WILDCARD_SEARCHSET)
  },
  {
    condition: (params) => ['A20047'].includes(params.gp) && ['Me*'].includes(params.family) && (params.birthDate[0]) === 'eq2015-10-22',
    action: () => timestampBody(GP_SEARCHSET)
  },
  {
    condition: (params) => params.deathDate === 'le2019-02-28' && ['TUNNEY'].includes(params.family) && (params.birthDate[0]) === 'ge1980-01-01',
    action: () => timestampBody(DEATHDATE_SEARCHSET)
  },
  {
    condition: (params) => params.family === 'McMatch-Single' && params.postalCode === 'BAP 4WG' && (params.birthDate[0]) === '1954-10-26' &&
     params.gender === 'male',
    action: () => timestampBody(MOCK_SINGLE_SEARCHSET)
  },
  {
    condition: (params) => params.family === 'McMatch-Multiple' && params.postalCode === 'DN19 7UD' && (params.birthDate[0]) === '1997-08-20',
    action: () => timestampBody(MOCK_MULTIPLE_SEARCHSET)
  },
  {
    condition: (params) => params.family === 'Jones' && params.gender === 'male' && (params.birthDate[0]) === 'ge1992-01-01',
    action: () => timestampBody(JACKIE_JONES_SEARCHSET)
  },
  {
    condition: (params) => params.family === 'Godsoe' && params.gender === 'male' && (params.birthDate[0]) === 'eq1936-02-24',
    action: () => timestampBody(RODNEY_GODSOE_SEARCHSET)
  },
  {
    condition: (params) => params.family === 'Massam' && (params.birthDate[0] === 'eq1920-08-11' || params.birthDate[0] === 'le1920-08-11'),
    action: () => timestampBody(MARTHA_MASSAM_SEARCHSET)
  },
  {
    condition: (params) => params.family === 'YOUDS' && params.maxResults === '1',
    action: () => TOO_MANY_MATCHES
  },
  {
    condition: (params) => params.family === 'YOUDS',
    action: () => timestampBody(YOUDS_SEARCHSET)
  }
  // Add additional match cases for other conditions
]

if (request.pathMatches('/Patient') && request.get) {
  response.headers = basicResponseHeaders(request)
  const params = {
    family: request.param('family'),
    given: request.params.given || [],
    gender: request.param('gender'),
    birthDate: request.params.birthdate || [],
    postalCode: request.param('address-postalcode'),
    fuzzyMatch: request.paramBool('_fuzzy-match'),
    phone: request.param('phone'),
    email: request.param('email'),
    maxResults: request.param('_max-results'),
    historyMatch: request.param('_history'),
    gp: request.param('general-practitioner'),
    deathDate: request.param('death-date'),
    request
  }

  if (validateHeaders(request) && validateQueryParams(request)) {
    const matchedCase = matchCases.find(caseObj => caseObj.condition(params))

    if (matchedCase) {
      response.body = matchedCase.action()
    } else {
      response.body = timestampBody(EMPTY_SEARCHSET)
    }
  }
}
