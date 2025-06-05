package patients

import com.intuit.karate.gatling.PreDef._
import io.gatling.core.Predef._
import scala.concurrent.duration._

class GetPatientByDefaultTestAppSimulation extends Simulation {
  var users = 6
  var duration = 1
  
  val protocol = karateProtocol()
  
    protocol.runner.karateEnv("veit07")
    
    // track the index of the request that returns 429
  var requestCounter = 0
  var all429s: Seq[Int] = Seq()

  val scn = scenario("RateLimitTest")
    .exec(session => {
      requestCounter += 1
      session.set("requestIndex", requestCounter)
    })
    .exec(karateFeature("classpath:patients/rateLimits/getPatientDetails/getPatientForDefaultApp.feature"))
    .exec { session =>
      if (session.contains("is429") && session("is429").as[Boolean]) {
      all429s = all429s :+ session("requestIndex").as[Int]
      }
      session
    }
    
    setUp(
      scn.inject(constantUsersPerSec(users) during (duration second)).protocols(protocol)
    )
  
  // hook to run after simulation ends
  after {
    println("=== Simulation Complete ===")
    println(s"Total requests from default Test app: ${users}")
    if (all429s.nonEmpty) {
      println(s"Total 429 responses: ${all429s.size}")
    }else {
      println("No 429 responses received")
    }
  }
}
