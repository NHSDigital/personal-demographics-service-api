 if (context.flow === 'TARGET_REQ_FLOW') {
  var path = context.getVariable('proxy.pathsuffix')
  var fixedpath = ""
  if(path.startsWith("/FHIR/R4"))
  {
   fixedpath = path.slice(9);   //Length of /FHIR/R4
  }
  else
  {
     fixedpath = path; 
  }
  
  context.setVariable('fixedpath', fixedpath)
}
