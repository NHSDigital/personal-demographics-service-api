package patients.appRestricted;

import com.intuit.karate.junit5.Karate;

class AppRestrictedTests {
    
    @Karate.Test
    Karate testGetPatient() {
        return Karate.run("getPatient").tags("~@ignore").relativeTo(getClass());
    }  

}
