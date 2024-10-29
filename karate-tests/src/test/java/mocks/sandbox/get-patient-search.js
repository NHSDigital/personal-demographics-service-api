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
  if (request.param('phone') && request.param('phone') !== '01632960587') return false
  if (request.param('email') && request.param('email') !== 'jane.smith@example.com') return false
  return true
}

/*
    Handler for search Patient functionality
*/
if (request.pathMatches('/Patient') && request.get) {
  response.headers = basicResponseHeaders(request)

  const family = request.param('family')
  const given = request.params.given || []
  const gender = request.param('gender')
  const birthDate = request.params.birthdate || []
  const postalCode = request.param('address-postalcode')
  const fuzzyMatch = request.paramBool('_fuzzy-match')
  const phone = request.param('phone')
  const email = request.param('email')
  const maxResults = request.param('_max-results')
  const historyMatch = request.param('_history')
  const gp = request.param('general-practitioner')
  const deathDate = request.param('death-date')

  if (validateHeaders(request) && validateQueryParams(request)) {
    if (fuzzyMatch) {
      if (family === 'Blogs' && given[0] === 'Joe' && birthDate[0] === '1955-11-05') {
        response.body = timestampBody(JOE_BLOGS_HISTORIC_NAME_SEARCHSET)
      } else if (family === 'ATTSÖN' && (given[0]) === 'PÀULINÉ' && birthDate[0] === '1960-07-14') {
        response.body = timestampBody(PAULINE_ATTISON_SEARCHSET)
      } else if (phone === '01222111111' && email === 'test@test.com') {
        response.body = timestampBody(FUZZY_SINGLE_SEARCHSET)
      } else if (family === 'Smythe' && (given[0]) === 'Mat' && (birthDate[0]) === 'ge2000-05-03' && gender === 'male' && postalCode === 'DN17 4AA' && email !== 'rubbish@work.com') {
        response.body = timestampBody(FUZZY_MULTI_SEARCHSET)
      } else if (['MED', 'HUME'].includes(family) && (given[0]) === 'Casey' && (birthDate[0]) === '1999-09-09') {
        response.body = timestampBody(HISTORIC_DATA_SEARCHSET)
      } else if (family === 'MED' && (given[0]) === 'Casey' && (birthDate[0]) === '2024-01-12') {
        response.body = timestampBody(EMPTY_SEARCHSET)
      } else if (family === 'LEEKE' && (given[0]) === 'Horace' && (birthDate[0]) === '1956-05-02' && postalCode === 'DN16') {
        response.body = timestampBody(EMPTY_SEARCHSET)
      } else if (!phone && !email) {
        response.body = timestampBody(FUZZY_SEARCH_PATIENT_17)
      } else if (phone === '01632960587' && !email) {
        response.body = timestampBody(janeSmithSearchsetWithScore(0.9124))
      } else if (email === 'jane.smith@example.com' && !phone) {
        response.body = timestampBody(janeSmithSearchsetWithScore(0.9124))
      } else if (phone === '01632960587' && email === 'jane.smith@example.com') {
        response.body = timestampBody(janeSmithSearchsetWithScore(0.9542))
      } else {
        response.body = timestampBody(EMPTY_SEARCHSET)
      }
    } else if (historyMatch) {
      if (['Smith', 'smith'].includes(family) && ['Male', 'male'].includes(gender) && (birthDate[0]) === 'eq2000-05-05' && email === 'Historic@historic.com') {
        response.body = timestampBody(HISTORIC_EMAIL_SEARCHSET)
      } else if (['HUME'].includes(family) && (birthDate[0]) === '1999-09-09') {
        response.body = timestampBody(HISTORIC_DATA_SEARCHSET)
      } else if (family === 'MED' && (birthDate[0]) === '2024-01-12') {
        response.body = timestampBody(EMPTY_SEARCHSET)
      }
    } else if (['Sm*', 'sm*'].includes(family)) {
      if (!phone && !email) {
        if (!maxResults) {
          response.body = timestampBody(WILDCARD_SEARCH)
        } else if (parseInt(maxResults) < 2) {
          response.body = context.read('classpath:mocks/stubs/searchResponses/TOO_MANY_MATCHES.json')
        }
      } else if (phone === '01632960587' && !email) {
        response.body = timestampBody(janeSmithSearchsetWithScore(1))
      } else if (email === 'jane.smith@example.com' && !phone) {
        response.body = timestampBody(janeSmithSearchsetWithScore(1))
      } else if (email === 'jane.smith@example.com' && phone === '01632960587') {
        response.body = timestampBody(janeSmithSearchsetWithScore(1))
      } else if (email === 'janet.smythe@example.com') {
        response.body = timestampBody(janeSmithSearchsetWithScore(1))
      } else if (email === 'test@test.com' && phone === '01234123123' && (birthDate[0]) === 'eq2000-05-05') {
        response.body = timestampBody(MULTIMATCHWITHPHONEANDEMAIL_SEARCHSET)
      } else {
        response.body = timestampBody(EMPTY_SEARCHSET)
      }
    } else if (['Smythe', 'smythe'].includes(family)) {
      response.body = timestampBody(RESTRICTED_PATIENT_SEARCH)
    // using eqeqeq to compare birthDates doesn't work here
    // eslint-disable-next-line eqeqeq
    } else if (['Smith', 'smith'].includes(family) && ['Female', 'female'].includes(gender) && (birthDate[0] === 'eq2010-10-22' || (birthDate[0] === 'ge2010-10-21' && birthDate[1] === 'le2010-10-23')) && otherJaneSmithParamsAreValid(request)) {
      response.body = timestampBody(SIMPLE_SEARCH)
    } else if (['Smith', 'smith'].includes(family) && ['Male', 'male'].includes(gender) && (given[0]) === 'John Paul' && given[1] === 'James') {
      response.body = timestampBody(JOHN_PAUL_SMITH_SEARCHSET)
    } else if (['CUFF', 'Cuff'].includes(family) && ['Female', 'female'].includes(gender) && (birthDate[0] === 'eq1926-01-07')) {
      response.body = timestampBody(CUFF_SUPERSEDED_SEARCHSET)
    } else if (['Smith', 'smith'].includes(family) && ['Male', 'male'].includes(gender) && (birthDate[0]) === 'eq2000-05-05' && (given[0]) === 'Sam' && (given[1]) === 'Bob') {
      response.body = timestampBody(OTHER_GIVENNAME_SEARCHSET)
    } else if (['Smith', 'smith'].includes(family) && ['Male', 'male'].includes(gender) && (birthDate[0]) === 'eq2000-05-05' && phone === '01234123123' && email === 'test@test.com') {
      response.body = timestampBody(MULTIMATCHWITHPHONEANDEMAIL_SEARCHSET)
    } else if (['Muir', 'Muir'].includes(family) && ['Male', 'male'].includes(gender) && (birthDate[0]) === 'eq2017-09-06' && phone === '00917855986859') {
      response.body = timestampBody(COUNTRYCODE_SEARCHSET)
    } else if (['DN17*'].includes(postalCode) && ['Smith', 'smith'].includes(family) && ['Male', 'male'].includes(gender) && (birthDate[0]) === 'eq2000-05-05') {
      response.body = timestampBody(POSTALCODE_WILDCARD_SEARCHSET)
    } else if (['A20047'].includes(gp) && ['Me*'].includes(family) && (birthDate[0]) === 'eq2015-10-22') {
      response.body = timestampBody(GP_SEARCHSET)
    } else if (deathDate === 'le2019-02-28' && ['TUNNEY'].includes(family) && (birthDate[0]) === 'ge1980-01-01') {
      response.body = timestampBody(DEATHDATE_SEARCHSET)
    } else {
      response.body = timestampBody(EMPTY_SEARCHSET)
    }
    // stubs used for the post patient tests
    if (family === 'McMatch-Single' && postalCode === 'BAP 4WG' && (birthDate[0]) === '1954-10-26' && gender === 'male') {
      response.body = timestampBody(MOCK_SINGLE_SEARCHSET)
    }
    if (family === 'McMatch-Multiple' && postalCode === 'DN19 7UD' && (birthDate[0]) === '1997-08-20') {
      response.body = timestampBody(MOCK_MULTIPLE_SEARCHSET)
    }
    // stubs used for the search tests
    if (family === 'Jones' && gender === 'male' && (birthDate[0]) === 'ge1992-01-01') {
      response.body = timestampBody(JACKIE_JONES_SEARCHSET)
    }
    if (family === 'Godsoe' && gender === 'male' && (birthDate[0]) === 'eq1936-02-24') {
      response.body = timestampBody(RODNEY_GODSOE_SEARCHSET)
    }
    if (family === 'Massam' && (birthDate[0] === 'eq1920-08-11' || birthDate[0] === 'le1920-08-11')) {
      response.body = timestampBody(MARTHA_MASSAM_SEARCHSET)
    }
    if (family === 'YOUDS') {
      if (maxResults === '1') {
        response.body = context.read('classpath:mocks/stubs/searchResponses/TOO_MANY_MATCHES.json')
      } else {
        response.body = timestampBody(YOUDS_SEARCHSET)
      }
    }
  }
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
    condition: (params) => params.fuzzyMatch && params.family === 'Smythe' && (given[0]) === 'Mat' && (birthDate[0]) === 'ge2000-05-03' && gender === 'male' && postalCode === 'DN17 4AA' && email !== 'rubbish@work.com',
    action: () => timestampBody(FUZZY_SINGLE_SEARCHSET)
  },
  // Add additional cases as needed
  {
    condition: (params) => ['Smith', 'smith'].includes(params.family) && ['Female', 'female'].includes(params.gender) &&
      (params.birthDate[0] === 'eq2010-10-22' || (params.birthDate[0] === 'ge2010-10-21' && params.birthDate[1] === 'le2010-10-23')) && otherJaneSmithParamsAreValid(params.request),
    action: () => timestampBody(SIMPLE_SEARCH)
  },
  {
    condition: (params) => params.family === 'YOUDS' && params.maxResults === '1',
    action: () => context.read('classpath:mocks/stubs/searchResponses/TOO_MANY_MATCHES.json')
  },
  {
    condition: (params) => params.family === 'YOUDS',
    action: () => timestampBody(YOUDS_SEARCHSET)
  }
  // Add additional match cases for other conditions
];

function handleRequest(request, response) {
  if (request.pathMatches('/Patient') && request.get) {
    response.headers = basicResponseHeaders(request);

    // Validation
    if (!(validateHeaders(request) && validateQueryParams(request))) return;

    // Match response based on defined conditions
    const matchedResponse = responseMap.find((entry) => entry.condition(request)).response;
    response.body = timestampBody(matchedResponse);
  }
}