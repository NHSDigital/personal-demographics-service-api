package schemas.schemaTests;

import com.intuit.karate.junit5.Karate;

public class schemaTestsRunner {
        
    @Karate.Test
    Karate testAddressSchema() {
        return Karate.run("addressSchema").relativeTo(getClass());
    }    

    @Karate.Test
    Karate testContactPointSchema() {
        return Karate.run("contactPointSchema").relativeTo(getClass());
    }    

    @Karate.Test
    Karate testGeneralPractitionerReferenceSchema() {
        return Karate.run("generalPractitionerReferenceSchema").relativeTo(getClass());
    }    

    @Karate.Test
    Karate testHumanNameSchema() {
        return Karate.run("humanNameSchema").relativeTo(getClass());
    }    

    @Karate.Test
    Karate testPatientNhsNumberAllocationSchema() {
        return Karate.run("patientNhsNumberAllocationSchema").relativeTo(getClass());
    }    

}