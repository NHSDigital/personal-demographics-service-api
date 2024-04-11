package patients.healthcareWorker.getPatientDetails;

import com.intuit.karate.junit5.Karate;

public class GetPatientDetailsTests {
    
    @Karate.Test
    Karate testGetPatientErrorScenarios() {
        return Karate.run("getPatientErrorScenarios").relativeTo(getClass());
    }    
}
