package patients.appRestricted;

import com.intuit.karate.junit5.Karate;

class AppRestrictedTests {
    
    @Karate.Test
    Karate testGetPatient() {
        return Karate.run("getPatient").relativeTo(getClass());
    }  

    @Karate.Test
    Karate testCreatePatient() {
        return Karate.run("createPatientError").relativeTo(getClass());
    }  

}
