package patients

import com.intuit.karate.gatling.PreDef._
import io.gatling.core.Predef._
import scala.concurrent.duration._


class PatientsSimulation extends Simulation {
  
  val protocol = karateProtocol(
      "/Patient" -> pauseFor("patch" -> 0)
    )
  
    protocol.runner.karateEnv("perf")
  
    val post = scenario("post").exec(karateFeature("classpath:patients/healthcareWorker/postPatient.feature"))
    
    setUp(
      post.inject(rampUsers(60) during (10 seconds)).protocols(protocol),
    )
  
}
