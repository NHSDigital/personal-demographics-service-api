/*
    Supporting functions for building responses
*/

/* Karate objects */
/* global context, request, response */

/* Functions defined in supporting-functions.js */
/* global validateHeaders, setInvalidSearchDataError, setMissingValueError, basicResponseHeaders */

/* Constants defined in stubs.js */
/* global EMPTY_SEARCHSET, SEARCH_PATIENT_9000000009, FUZZY_SEARCH_PATIENT_17, WILDCARD_SEARCH, RESTRICTED_PATIENT_SEARCH, SIMPLE_SEARCH, COMPOUND_NAME_SEARCH */

const MOCK_SINGLE_SEARCHSET = context.read('classpath:mocks/stubs/searchResponses/mock_single_searchset.json')
const MOCK_MULTIPLE_SEARCHSET = context.read('classpath:mocks/stubs/searchResponses/mock_multiple_searchset.json')

/*
 * These stubs are used for our search tests
 */
const JACKIE_JONES_SEARCHSET = context.read('classpath:mocks/stubs/searchResponses/jackie_jones_searchset.json')
const RODNEY_GODSOE_SEARCHSET = context.read('classpath:mocks/stubs/searchResponses/rodney_godsoe_searchset.json')
const MARTHA_MASSAM_SEARCHSET = context.read('classpath:mocks/stubs/searchResponses/martha_massam_searchset.json')
const YOUDS_SEARCHSET = context.read('classpath:mocks/stubs/searchResponses/youds_searchset.json')
const BILL_GARTON_SEARCHSET = context.read('classpath:mocks/stubs/searchResponses/bill_garton_searchset.json')
const PAULINE_ATTISON_SEARCHSET = context.read('classpath:mocks/stubs/searchResponses/pauline_attison_searchset.json')

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
  Add a timestamp to the body of the response
*/
function timestampBody (body) {
  // timestamp format is '2019-12-25T12:00:00+00:00'
  body.timestamp = new Date().toISOString()
  return body
}

/*
    Specific query param validation to support main handler
*/
function validateQueryParams (request) {
  const NOT_ENOUGH_SEARCH_PARAMS = 'Not enough search parameters were provided for a valid search, you must supply family and birthdate as a minimum and only use recognised parameters from the api catalogue.'

  const REQUIRED_PARAMS = [
    'family', 'birthdate'
  ]
  const VALID_PARAMS = [
    '_fuzzy-match', '_exact-match', '_history', '_max-results',
    'family', 'given', 'gender', 'birthdate', 'death-date',
    'address-postcode', 'address-postalcode', 'general-practitioner', 'email', 'phone'
  ]

  // check the validity of certain params first
  const birthDateArray = request.params.birthdate
  if (birthDateArray) {
    for (const index in birthDateArray) {
      const birthDate = birthDateArray[index]
      if (!birthDate || !birthDate.match(/^(eq|ge|le)?[0-9]{4}-[0-9]{2}-[0-9]{2}$/)) {
        const diagnostics = `Invalid value - '${birthDate}' in field 'birthdate'`
        return setInvalidSearchDataError(diagnostics)
      }
    }
  }

  // ignore any params that we don't handle
  const validParams = []
  for (const paramName in request.params) {
    if (VALID_PARAMS.includes(paramName)) {
      validParams.push(paramName)
    }
  }
  for (const index in REQUIRED_PARAMS) {
    if (!validParams.includes(REQUIRED_PARAMS[index])) {
      return setMissingValueError(NOT_ENOUGH_SEARCH_PARAMS)
    }
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
  const given = request.params.given
  const gender = request.param('gender')
  const birthDate = request.params.birthdate
  const postalCode = request.param('address-postalcode')
  const fuzzyMatch = request.paramBool('_fuzzy-match')
  const phone = request.param('phone')
  const email = request.param('email')
  const maxResults = request.param('_max-results')

  context.log('********************************************')
  context.log('family:', family)
  context.log('given:', given)
  context.log('gender: ', gender)
  context.log('birthDate: ', birthDate)
  context.log('********************************************')

  if (validateHeaders(request) && validateQueryParams(request)) {
    if (fuzzyMatch) {
      if (family === 'Garton' && given[0] === 'Bill' && birthDate[0] === '1946-06-23') {
        response.body = timestampBody(BILL_GARTON_SEARCHSET)
      } else if (family === 'ATTSÖN' && given[0] === 'PÀULINÉ' && birthDate[0] === '1960-07-14') {
        response.body = timestampBody(PAULINE_ATTISON_SEARCHSET)
      } else if (!phone && !email) {
        response.body = timestampBody(FUZZY_SEARCH_PATIENT_17)
      } else if (phone === '01632960587' && !email) {
        response.body = timestampBody(janeSmithSearchsetWithScore(0.9124))
      } else if (email === 'jane.smith@example.com' && !phone) {
        response.body = timestampBody(janeSmithSearchsetWithScore(0.9124))
      } else if (phone === '01632960587' && email === 'jane.smith@example.com') {
        response.body = timestampBody(janeSmithSearchsetWithScore(0.9542))
      }
    } else if (['Sm*', 'sm*'].includes(family)) {
      if (!phone && !email) {
        response.body = timestampBody(WILDCARD_SEARCH)
      } else if (phone === '01632960587' && !email) {
        response.body = timestampBody(janeSmithSearchsetWithScore(1))
      } else if (email === 'jane.smith@example.com' && !phone) {
        response.body = timestampBody(janeSmithSearchsetWithScore(1))
      }
    } else if (['Smythe', 'smythe'].includes(family)) {
      response.body = timestampBody(RESTRICTED_PATIENT_SEARCH)
    // using eqeqeq to compare birthDates doesn't work here
    // eslint-disable-next-line eqeqeq
    } else if (['Smith', 'smith'].includes(family) && ['Female', 'female'].includes(gender) && (birthDate == 'eq2010-10-22' || birthDate == 'ge2010-10-21,le2010-10-23') && otherJaneSmithParamsAreValid(request)) {
      response.body = timestampBody(SIMPLE_SEARCH)
    } else if (['Smith', 'smith'].includes(family) && ['Male', 'male'].includes(gender) && given[0] === 'John Paul' && given[1] === 'James') {
      response.body = timestampBody(COMPOUND_NAME_SEARCH)
    } else {
      response.body = timestampBody(EMPTY_SEARCHSET)
    }
    // stubs used for the post patient tests
    if (family === 'McMatch-Single' && postalCode === 'BAP4WG' && birthDate[0] === '1954-10-26' && gender === 'male') {
      response.body = timestampBody(MOCK_SINGLE_SEARCHSET)
    }
    if (family === 'McMatch-Multiple' && postalCode === 'DN19 7UD' && birthDate[0] === '1997-08-20') {
      response.body = timestampBody(MOCK_MULTIPLE_SEARCHSET)
    }
    // stubs used for the search tests
    if (family === 'Jones' && gender === 'male' && birthDate[0] === 'ge1992-01-01') {
      response.body = timestampBody(JACKIE_JONES_SEARCHSET)
    }
    if (family === 'Godsoe' && gender === 'male' && birthDate[0] === 'eq1936-02-24') {
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
