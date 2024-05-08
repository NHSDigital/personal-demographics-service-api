package patients.patientAccess;

import com.intuit.karate.junit5.Karate;

public class TestPatientAccess {
    
    // static HttpServer server;

    // @BeforeAll
    // static void beforeAll() {
    //     String env = System.getProperty("karate.env", "veit07");
    //     if (env.equals("mock")) {
    //         server = MockRunner.start("src/test/java/mocks", 8080);
    //     }
    // }

    @Karate.Test
    Karate testPostPatientError() {
        return Karate.run("postPatientError").relativeTo(getClass());
    }

}