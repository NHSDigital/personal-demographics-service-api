/*
    Supporting functions for building responses
*/

/* Karate objects */
/* global request, response */

/* Functions defined in supporting-functions.js */
/* global validateHeaders, setInvalidSearchDataError, setMissingValueError, basicResponseHeaders */

/* Constants defined in stubs.js */
/* global EMPTY_SEARCHSET, SEARCH_PATIENT_9000000009, FUZZY_SEARCH_PATIENT_17, WILDCARD_SEARCH, RESTRICTED_PATIENT_SEARCH, SIMPLE_SEARCH, COMPOUND_NAME_SEARCH */

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
    'family', 'gender', 'birthdate'
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
  const fuzzyMatch = request.paramBool('_fuzzy-match')
  const phone = request.param('phone')
  const email = request.param('email')

  if (validateHeaders(request) && validateQueryParams(request)) {
    if (fuzzyMatch) {
      if (!phone && !email) {
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
  }
}
