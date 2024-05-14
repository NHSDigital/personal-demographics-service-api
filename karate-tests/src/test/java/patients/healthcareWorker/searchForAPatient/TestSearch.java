package patients.healthcareWorker.searchForAPatient;

import com.intuit.karate.junit5.Karate;

public class TestSearch {
     
    @Karate.Test
    Karate testSearchParams() {
        return Karate.run("searchParams").relativeTo(getClass());
    }   

    @Karate.Test
    Karate testSearchErrors() {
        return Karate.run("searchErrors").relativeTo(getClass());
    }   

}
