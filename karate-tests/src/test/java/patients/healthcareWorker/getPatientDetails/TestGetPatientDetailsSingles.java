package patients.healthcareWorker.getPatientDetails;

import com.intuit.karate.junit5.Karate;


public class TestGetPatientDetailsSingles {

    @Karate.Test
    Karate testGetPatientByNHSNumber() {
        return Karate.run("getPatientByNHSNumber").relativeTo(getClass());
    }    
    
    @Karate.Test
    Karate testGetPatientErrorScenarios() {
        return Karate.run("getPatientErrorScenarios").relativeTo(getClass());
    }    
}
