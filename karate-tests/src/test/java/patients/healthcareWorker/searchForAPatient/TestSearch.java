package patients.healthcareWorker.searchForAPatient;

import com.intuit.karate.junit5.Karate;

public class TestSearch {
 
    @Karate.Test
    Karate testSimpleSearch() {
        return Karate.run("simpleSearch").relativeTo(getClass());
    }   
}
