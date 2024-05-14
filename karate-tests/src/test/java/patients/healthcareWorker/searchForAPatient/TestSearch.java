package patients.healthcareWorker.searchForAPatient;

import org.junit.jupiter.api.BeforeAll;

import com.intuit.karate.http.HttpServer;
import com.intuit.karate.junit5.Karate;

import mocks.MockRunner;

public class TestSearch {

    static HttpServer server;

    @BeforeAll
    static void beforeAll() {
        String env = System.getProperty("karate.env", "veit07");
        if (env.equals("mock")) {
            server = MockRunner.start("src/test/java/mocks", 8080);
        }
    }  
    
    @Karate.Test
    Karate testSearchParams() {
        return Karate.run("searchParams").relativeTo(getClass());
    }

    @Karate.Test
    Karate testSearchErrors() {
        return Karate.run("searchErrors").relativeTo(getClass());
    }   

}
