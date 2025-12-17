/*
 * For APM-1616: Explain invalid access tokens more clearly.
 */

const auth = context.getVariable("request.header.authorization");
var faultstring = context.getVariable("faultstring");
if (auth === null){
  faultstring = "Missing Authorization header";
}
else if (auth === ""){
  faultstring = "Empty Authorization header";
}
else {
  const authWords = auth.split(" ");
  if (authWords.length === 0){
    faultstring = "Invalid Authorization header";
  }
  else if (authWords.length === 1){
    faultstring = "Missing access token";
  }
  else if (authWords[0] !== "Bearer"){
    faultstring = "Invalid token type '" + authWords[0] + "', must be 'Bearer'";
  }
}
context.setVariable("faultstring", faultstring);
