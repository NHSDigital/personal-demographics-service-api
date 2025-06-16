Feature:

Scenario:
    * url baseURL
    * configure headers = call read('classpath:auth/auth-headers.js') 
    * header Content-Type = "application/json-patch+json"
    * header If-Match = etag
    * path endpoint
    * request requestBody
    * method patch
    * status 200