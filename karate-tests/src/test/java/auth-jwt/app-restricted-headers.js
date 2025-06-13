function fn() {
  var accessToken = karate.get('accessToken')
  var correlation_id = '' + java.util.UUID.randomUUID();
  var request_id = '' + java.util.UUID.randomUUID();

  var headers = {
    "nhsd-session-id": "123",
    "x-request-id": request_id,
    "x-correlation-id": correlation_id,
    "authorization": "Bearer " + accessToken
  }

  return headers;
}