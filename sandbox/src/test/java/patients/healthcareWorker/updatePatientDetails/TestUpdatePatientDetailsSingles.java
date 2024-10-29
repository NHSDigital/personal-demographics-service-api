package patients.healthcareWorker.updatePatientDetails;

import org.junit.jupiter.api.BeforeAll;

import com.intuit.karate.http.HttpServer;
import com.intuit.karate.junit5.Karate;

import mocks.MockRunner;

public class TestUpdatePatientDetailsSingles {

    static HttpServer server;

    @BeforeAll
    static void beforeAll() {
        String env = System.getProperty("karate.env", "veit07");
        if (env.equals("mock")) {
            server = MockRunner.start("src/test/java/mocks", 8080);
        }
    }

    @Karate.Test
    Karate testAddAndRemove() {
        return Karate.run("addAndRemove").relativeTo(getClass());
    }

    @Karate.Test
    Karate testAddErrors() {
        return Karate.run("addErrors").relativeTo(getClass());
    }

    @Karate.Test
    Karate testRemoveErrors() {
        return Karate.run("removeErrors").relativeTo(getClass());
    }

    @Karate.Test
    Karate testReplace() {
        return Karate.run("replace").relativeTo(getClass());
    }

    @Karate.Test
    Karate testReplaceErrors() {
        return Karate.run("replaceErrors").relativeTo(getClass());
    }

    @Karate.Test
    Karate testRequestErrors() {
        return Karate.run("requestErrors").relativeTo(getClass());
    }

}
