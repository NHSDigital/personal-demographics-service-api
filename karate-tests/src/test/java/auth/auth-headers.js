function fn() {
  let client_id = karate.get('clientID');
  let accessToken = karate.get('accessToken')
  let correlation_id = '' + java.util.UUID.randomUUID(); 
  let request_id = '' + java.util.UUID.randomUUID(); 
  
  let headers = { 
    "client_id": client_id,
    "x-correlation-id": correlation_id,
    "x-request-id": request_id,
    "authorization": "Bearer " + accessToken
  }

  return headers;
}
