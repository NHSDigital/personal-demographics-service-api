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
const UNSUPPORTED_OPERATION_RESPONSE = context.read('classpath:mocks/stubs/errorResponses/NOT_SUPPORTED_SEARCH.json')
const EXACT_MATCH_SEARCHSET = context.read('classpath:mocks/stubs/searchResponses/knap_kathy_exact_match.json')

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

  const params = Object.keys(request?.params ?? {})

  // check that params were actually provided
  if (params.length === 0) {
    setUnsupportedServiceError()
    return false
  }

  const { validParams, invalidParams } = splitValidAndInvalid(params, VALID_PARAMS)

  if (validateInvalidParams(invalidParams)) return false

  if (validateDateFields(request?.params)) return false

  if (validateRequiredFields(validParams)) return false

  return true
}

function splitValidAndInvalid (params, validList) {
  const validParams = []
  const invalidParams = []
  for (const paramName of params) {
    (validList.includes(paramName) ? validParams : invalidParams).push(paramName)
  }
  return { validParams, invalidParams }
}

function validateInvalidParams (invalidParams) {
  if (invalidParams.length === 3) {
    const diagnostics = "Invalid request with error - Additional properties are not allowed ('model', 'manufacturer', 'year' were unexpected)"
    setAdditionalPropertiesError(diagnostics)
    return true
  }
  if (invalidParams.length === 1) {
    const diagnostics = `Invalid request with error - Additional properties are not allowed ('${invalidParams[0]}' was unexpected)`
    setAdditionalPropertiesError(diagnostics)
    return true
  }
  return false
}

function validateDateFields (params) {
  for (const date of params?.birthdate ?? []) {
    if (!isValidDate(date)) {
      setInvalidValueError(`Invalid value - '${date}' in field 'birthdate'`)
      return true
    }
  }

  for (const date of params?.['death-date'] ?? []) {
    if (!isValidDate(date)) {
      setInvalidValueError(`Invalid value - '${date}' in field 'death-date'`)
      return true
    }
  }

  return false
}

function isValidDate (date) {
  return date?.match(/^(eq|ge|le)?\d{4}-\d{2}-\d{2}$/)
}

function validateRequiredFields (validParams) {
  if (!validParams?.includes('birthdate')) {
    setMissingValueError("Missing value - 'birth_date/birth_date_range_start/birth_date_range_end'")
    return true
  }
  if (!validParams?.includes('family')) {
    setInvalidSearchDataError(
      "Invalid search data provided - 'No searches were performed as the search criteria did not meet the minimum requirements'"
    )
    return true
  }
  return false
}

function otherJaneSmithParamsAreValid (request) {
  const phone = request.param('phone')
  const email = request.param('email')
  return (!phone || phone === '01632960587') && (!email || email === 'jane.smith@example.com')
}

function extractBirthDate (params) {
  return params.birthDate?.[0]?.replace(/^eq/, '')
}
function extractDeathDate (params) {
  return params.deathDate?.[0]?.replace(/^eq/, '')
}
// Define match cases as functions
const matchCases = [
  {
    condition: (params) => params.fuzzyMatch && params.family === 'Blogs' && params.given[0] === 'Joe' && extractBirthDate(params) === '1955-11-05',
    action: () => timestampBody(JOE_BLOGS_HISTORIC_NAME_SEARCHSET)
  },
  // Unicode search
  {
    condition: (params) => params.fuzzyMatch && params.family === 'ATTSÖN' && params.given[0] === 'PÀULINÉ' && extractBirthDate(params) === '1960-07-14',
    action: () => timestampBody(PAULINE_ATTISON_SEARCHSET)
  },
  {
    condition: (params) => params.fuzzyMatch && params.phone === '01222111111' && params.email === 'test@test.com',
    action: () => timestampBody(FUZZY_SINGLE_SEARCHSET)
  },
  // Algorithm search with basic(given name, gender, date of birth and postal code) and phone number - no match -> single match -> multi match
  {
    condition: (params) => params.fuzzyMatch && params.family === 'Smythe' && params.given[0] === 'Mat' && (extractBirthDate(params)) === 'ge2000-05-03' &&
     params.gender === 'male' &&
     params.postalCode === 'DN17 4AA' && params.email !== 'rubbish@work.com',
    action: () => timestampBody(FUZZY_MULTI_SEARCHSET)
  },
  // Algorithm search with basic(given name, gender, date of birth and postal code) and phone number - no match -> single match -> multi match
  {
    condition: (params) => params.fuzzyMatch && params.family === 'Smythe' && params.given[0] === 'Mat' && (extractBirthDate(params)) === 'ge2000-05-03' &&
     params.gender === 'male' &&
     params.postalCode === 'DN17 4AA' && params.email === 'rubbish@work.com',
    action: () => timestampBody(EMPTY_SEARCHSET)
  },
  // Fuzzy matching should not return historic matches when historic dob is sent as query parameter
  {
    condition: (params) => params.fuzzyMatch && ['MED', 'HUME'].includes(params.family) && params.given[0] === 'Casey' && (extractBirthDate(params)) === '1999-09-09',
    action: () => timestampBody(HISTORIC_DATA_SEARCHSET)
  },
  {
    condition: (params) => params.fuzzyMatch && params.family === 'MED' && params.given[0] === 'Casey' && (extractBirthDate(params)) === '2024-01-12',
    action: () => timestampBody(EMPTY_SEARCHSET)
  },
  // Historic matching shouldn't return hidden matches
  {
    condition: (params) => params.fuzzyMatch && params.family === 'LEEKE' && params.given[0] === 'Horace' && (extractBirthDate(params)) === '1956-05-02' &&
     params.postalCode === 'DN16',
    action: () => timestampBody(EMPTY_SEARCHSET)
  },
  // Fuzzy search
  {
    condition: (params) => params.fuzzyMatch && !params.phone && !params.email,
    action: () => timestampBody(FUZZY_SEARCH_PATIENT_17)
  },
  // Fuzzy search including phone
  {
    condition: (params) => params.fuzzyMatch && params.phone === '01632960587' && !params.email,
    action: () => timestampBody(janeSmithSearchsetWithScore(0.9124))
  },
  // Fuzzy search including email
  {
    condition: (params) => params.fuzzyMatch && params.email === 'jane.smith@example.com' && !params.phone,
    action: () => timestampBody(janeSmithSearchsetWithScore(0.9124))
  },
  // Fuzzy search including phone and email
  {
    condition: (params) => params.fuzzyMatch && params.phone === '01632960587' && params.email === 'jane.smith@example.com',
    action: () => timestampBody(janeSmithSearchsetWithScore(0.9542))
  },
  // Include history flag for non fuzzy search
  {
    condition: (params) => params.historyMatch && ['Smith', 'smith'].includes(params.family) && ['Male', 'male'].includes(params.gender) &&
    (extractBirthDate(params)) === '2000-05-05' && params.email === 'Historic@historic.com',
    action: () => timestampBody(HISTORIC_EMAIL_SEARCHSET)
  },
  // Exclude history flag for non fuzzy search
  {
    condition: (params) => ['Smith', 'smith'].includes(params.family) && ['Male', 'male'].includes(params.gender) &&
    (extractBirthDate(params)) === '2000-05-05' && (params.email === 'Historic@historic.com'),
    action: () => timestampBody(EMPTY_SEARCHSET)
  },
  // Simple and Alphanumeric search with email and phone number - no results
  {
    condition: (params) => ['Smith', 'smith', 'Sm*', 'sm*'].includes(params.family) && ['Male', 'male'].includes(params.gender) &&
    (extractBirthDate(params)) === '2000-05-05' && params.email === 'rubbish@test.com' && params.phone === '01234123123',
    action: () => timestampBody(EMPTY_SEARCHSET)
  },
  // Search for a PDS record based on historic DOB, family name, gender
  {
    condition: (params) => params.historyMatch && ['HUME'].includes(params.family) && (extractBirthDate(params)) === '1999-09-09',
    action: () => timestampBody(HISTORIC_DATA_SEARCHSET)
  },
  // Search for a PDS record based on historic DOB, family name, gender
  {
    condition: (params) => (params.family === 'MED' || ['HUME'].includes(params.family)) && (extractBirthDate(params) === '2024-01-12' || extractBirthDate(params) === '1999-09-09') &&
    (params.gender === 'male' || params.gender === 'female'),
    action: () => timestampBody(EMPTY_SEARCHSET)
  },
  // Wildcard search
  {
    condition: (params) => ['Sm*', 'sm*'].includes(params.family) && !params.phone && !params.email && !params.maxResults,
    action: () => timestampBody(WILDCARD_SEARCH)
  },
  // Search with limited results
  {
    condition: (params) => ['Sm*', 'sm*'].includes(params.family) && !params.phone && !params.email && Number.parseInt(params.maxResults) < 2,
    action: () => TOO_MANY_MATCHES
  },
  // Search with limited results inc phone
  {
    condition: (params) => ['Sm*', 'sm*'].includes(params.family) && params.phone && !params.email && Number.parseInt(params.maxResults) < 2,
    action: () => timestampBody(janeSmithSearchsetWithScore(1))
  },
  // Search with limited results inc email
  {
    condition: (params) => ['Sm*', 'sm*'].includes(params.family) && !params.phone && params.email && Number.parseInt(params.maxResults) < 2,
    action: () => timestampBody(janeSmithSearchsetWithScore(1))
  },
  // wildcard search including phone
  {
    condition: (params) => ['Sm*', 'sm*'].includes(params.family) && params.phone === '01632960587' && !params.email,
    action: () => timestampBody(janeSmithSearchsetWithScore(1))
  },
  // wildcard search including email
  {
    condition: (params) => ['Sm*', 'sm*'].includes(params.family) && params.email === 'jane.smith@example.com' && !params.phone,
    action: () => timestampBody(janeSmithSearchsetWithScore(1))
  },
  // wildcard search including email
  {
    condition: (params) => ['Sm*', 'sm*'].includes(params.family) && params.email === 'jane.smith@example.com' && params.phone === '01632960587',
    action: () => timestampBody(janeSmithSearchsetWithScore(1))
  },
  // Search with limited results inc phone
  {
    condition: (params) => ['Sm*', 'sm*'].includes(params.family) && params.email === 'janet.smythe@example.com',
    action: () => timestampBody(janeSmithSearchsetWithScore(1))
  },
  // Multiple matches with phone and email
  {
    condition: (params) => ['Sm*', 'sm*'].includes(params.family) && params.email === 'test@test.com' && params.phone === '01234123123' &&
     (extractBirthDate(params)) === '2000-05-05',
    action: () => timestampBody(MULTIMATCHWITHPHONEANDEMAIL_SEARCHSET)
  },
  // Restricted (sensitive) patient search
  {
    condition: (params) => ['Smythe', 'smythe'].includes(params.family),
    action: () => timestampBody(RESTRICTED_PATIENT_SEARCH)
  },
  // Search with date range, Basic search, Basic search including phone
  {
    condition: (params) => ['Smith', 'smith'].includes(params.family) && ['Female', 'female'].includes(params.gender) &&
    (extractBirthDate(params) === '2010-10-22' || (extractBirthDate(params) === 'ge2010-10-21' && params.birthDate[1] === 'le2010-10-23')) &&
     otherJaneSmithParamsAreValid(request),
    action: () => timestampBody(SIMPLE_SEARCH)
  },
  // Compound name search
  {
    condition: (params) => ['Smith', 'smith'].includes(params.family) && ['Male', 'male'].includes(params.gender) && params.given[0] === 'John Paul' &&
     params.given[1] === 'James',
    action: () => timestampBody(JOHN_PAUL_SMITH_SEARCHSET)
  },
  // Search should not return superseded patients record
  {
    condition: (params) => ['CUFF', 'Cuff'].includes(params.family) && ['Female', 'female'].includes(params.gender) &&
     (extractBirthDate(params) === '1926-01-07'),
    action: () => timestampBody(CUFF_SUPERSEDED_SEARCHSET)
  },
  {
    condition: (params) => ['Smith', 'smith'].includes(params.family) && ['Male', 'male'].includes(params.gender) &&
     (extractBirthDate(params)) === '2000-05-05' &&
     params.given[0] === 'Sam' && (params.given[1]) === 'Bob',
    action: () => timestampBody(OTHER_GIVENNAME_SEARCHSET)
  },
  // Simple and Alphanumeric search with email and phone number - Multi match
  {
    condition: (params) => ['Smith', 'smith'].includes(params.family) && ['Male', 'male'].includes(params.gender) &&
     (extractBirthDate(params)) === '2000-05-05' &&
     params.phone === '01234123123' && params.email === 'test@test.com',
    action: () => timestampBody(MULTIMATCHWITHPHONEANDEMAIL_SEARCHSET)
  },
  // Simple search with phone number including country code
  {
    condition: (params) => ['Muir', 'Muir'].includes(params.family) && ['Male', 'male'].includes(params.gender) &&
     (extractBirthDate(params)) === '2017-09-06' &&
     params.phone === '00917855986859',
    action: () => timestampBody(COUNTRYCODE_SEARCHSET)
  },
  // wildcard search on postcode
  {
    condition: (params) => ['DN17*'].includes(params.postalCode) && ['Smith', 'smith'].includes(params.family) &&
     ['Male', 'male'].includes(params.gender) &&
     (extractBirthDate(params)) === '2000-05-05',
    action: () => timestampBody(POSTALCODE_WILDCARD_SEARCHSET)
  },
  // Alphanumeric search with registered GP practice
  {
    condition: (params) => ['A20047'].includes(params.gp) && ['Me*'].includes(params.family) && (extractBirthDate(params)) === '2015-10-22',
    action: () => timestampBody(GP_SEARCHSET)
  },
  // Simple search with date of death parameter
  {
    condition: (params) => params.deathDate === 'le2019-02-28' && ['TUNNEY'].includes(params.family) && (extractBirthDate(params)) === 'ge1980-01-01',
    action: () => timestampBody(DEATHDATE_SEARCHSET)
  },
  {
    condition: (params) => params.family === 'McMatch-Single' && params.postalCode === 'BAP 4WG' && (extractBirthDate(params)) === '1954-10-26' &&
     params.gender === 'male',
    action: () => timestampBody(MOCK_SINGLE_SEARCHSET)
  },
  {
    condition: (params) => params.family === 'McMatch-Multiple' && params.postalCode === 'DN19 7UD' && (extractBirthDate(params)) === '1997-08-20',
    action: () => timestampBody(MOCK_MULTIPLE_SEARCHSET)
  },
  {
    condition: (params) => params.family === 'Jones' && params.gender === 'male' && (extractBirthDate(params)) === 'ge1992-01-01',
    action: () => timestampBody(JACKIE_JONES_SEARCHSET)
  },
  {
    condition: (params) => params.family === 'Godsoe' && params.gender === 'male' && (extractBirthDate(params)) === '1936-02-24',
    action: () => timestampBody(RODNEY_GODSOE_SEARCHSET)
  },
  {
    condition: (params) => params.family === 'Massam' && (extractBirthDate(params) === '1920-08-11' || extractBirthDate(params) === 'le1920-08-11'),
    action: () => timestampBody(MARTHA_MASSAM_SEARCHSET)
  },
  {
    condition: (params) => params.family === 'YOUDS' && params.maxResults === '1',
    action: () => TOO_MANY_MATCHES
  },
  {
    condition: (params) => params.family === 'YOUDS',
    action: () => timestampBody(YOUDS_SEARCHSET)
  },
  // Documentation example scenario
  {
    condition: (params) => ['Smith'].includes(params.family) && ['female'].includes(params.gender) && ['Jane'].includes(params.given) &&
    (extractBirthDate(params)) === '2010-10-22' && extractDeathDate(params) === '2010-10-22' && params.email === 'jane.smith@example.com' &&
    params.phone === '01632960587' && params.gp === 'Y12345' && params.postalCode === 'LS1 6AE',
    action: () => timestampBody(SEARCH_PATIENT_9000000009)
  },
  // Basic search with phone & email negative
  {
    condition: (params) => params.family === 'Smith' && params.gender === 'female' && (extractBirthDate(params)) === '2010-10-22' && params.email === 'deb.trotter@example.com' &&
    params.phone === '0121111111',
    action: () => timestampBody(EMPTY_SEARCHSET)
  },
  // Search on family name and DoB - No results
  {
    condition: (params) => (params.family === 'Spiderman' || params.family === 'Bingham') && (extractBirthDate(params) === '1962-07-31' || extractBirthDate(params) === '1934-12-18'),
    action: () => timestampBody(EMPTY_SEARCHSET)
  },
  // Include exact match flag for non fuzzy search
  {
    condition: (params) => params.exactMatch && ['KNAPP', 'Knapp', 'knapp'].includes(params.family) && ['Female', 'female'].includes(params.gender) &&
    (extractBirthDate(params)) === '1943-07-03',
    action: () => timestampBody(EXACT_MATCH_SEARCHSET)
  },
  // Exclude exact match flag for non fuzzy search
  {
    condition: (params) => ['KNAPP', 'Knapp', 'knap'].includes(params.family) && ['Female', 'female'].includes(params.gender) &&
    (extractBirthDate(params)) === '1943-07-03',
    action: () => timestampBody(EMPTY_SEARCHSET)
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
    postalCode: request.param('address-postalcode') || request.param('address-postcode'),
    fuzzyMatch: request.paramBool('_fuzzy-match'),
    phone: request.param('phone'),
    email: request.param('email'),
    maxResults: request.param('_max-results'),
    historyMatch: request.param('_history'),
    gp: request.param('general-practitioner'),
    deathDate: request.param('death-date'),
    exactMatch: request.param('_exact-match')
  }

  if (validateHeaders(request) && validateQueryParams(request)) {
    const matchedCase = matchCases.find(caseObj => caseObj.condition(params))

    if (matchedCase) {
      response.body = matchedCase.action()
    } else {
      response.body = timestampBody(UNSUPPORTED_OPERATION_RESPONSE)
    }
  }
}
