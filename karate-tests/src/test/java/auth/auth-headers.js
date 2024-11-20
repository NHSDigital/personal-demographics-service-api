function fn() {
  var client_id = karate.get('clientID');
  var accessToken = karate.get('accessToken')
  var correlation_id = '' + java.util.UUID.randomUUID(); 
  var request_id = '' + java.util.UUID.randomUUID(); 
  
  var headers = { 
    "client_id": client_id,
    "x-correlation-id": correlation_id,
    "x-request-id": request_id,
    "authorization": "Bearer " + accessToken
  }

  return headers;
}
