function fn() {
  const correlation_id = '' + java.util.UUID.randomUUID();
  const request_id = '' + java.util.UUID.randomUUID();

  return {
    "nhsd-session-id": "123",
    "x-request-id": request_id,
    "x-correlation-id": correlation_id,
  };
}