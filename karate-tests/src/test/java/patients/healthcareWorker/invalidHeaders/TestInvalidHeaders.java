package patients.healthcareWorker.invalidHeaders;

import com.intuit.karate.junit5.Karate;

public class TestInvalidHeaders {
    
    @Karate.Test
    Karate testInvalidHeaders() {
        return Karate.run("invalidHeaders").relativeTo(getClass());
    }   

}
