package patients

import com.intuit.karate.gatling.PreDef._
import io.gatling.core.Predef._
import scala.concurrent.duration._


class PatientsSimulation extends Simulation {
  
  val protocol = karateProtocol()
  
    protocol.runner.karateEnv("perf")
  
    val getSpecific = scenario("getSpecific").exec(karateFeature("classpath:patients/healthcareWorker/getPatient.feature"))
    val search = scenario("search").exec(karateFeature("classpath:patients/healthcareWorker/getPatient.feature"))
    
    setUp(
      getSpecific.inject(rampUsers(60) during (10 seconds)).protocols(protocol),
      search.inject(rampUsers(60) during (10 seconds)).protocols(protocol),
    )
  
}
