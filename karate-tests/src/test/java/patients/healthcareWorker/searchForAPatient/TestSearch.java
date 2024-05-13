package patients.healthcareWorker.searchForAPatient;

import com.intuit.karate.junit5.Karate;

public class TestSearch {
     
    @Karate.Test
    Karate testSearch() {
        return Karate.run("searchParams").relativeTo(getClass());
    }   

}
