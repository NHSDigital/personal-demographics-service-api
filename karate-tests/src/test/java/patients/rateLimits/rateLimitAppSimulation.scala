package patients

import com.intuit.karate.gatling.PreDef._
import io.gatling.core.Predef._
import scala.concurrent.duration._


class GetPatientByRateLimitAppSimulation extends Simulation {
val rateLimitAppRequests = Integer.getInteger("rateLimitAppRequests")
val duration = Integer.getInteger("duration")  
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
    .exec(karateFeature("classpath:patients/rateLimits/getPatientDetails/getPatientForRateLimitingApp.feature"))
    .exec { session =>
      if (session.contains("is429") && session("is429").as[Boolean]) {
      all429s = all429s :+ session("requestIndex").as[Int]
      }
      session
    }
    
    setUp(
      scn.inject(rampUsers(rateLimitAppRequests) during (duration.seconds)).protocols(protocol)
    )
  
  // hook to run after simulation ends
  after {
    println("=== Simulation Complete ===")
    println(s"Total requests from ratelimit Test app: ${rateLimitAppRequests}")
    if (all429s.nonEmpty) {
      println(s"Total 429 responses: ${all429s.size}")
    }else {
      println("No 429 responses received")
    }
  }
}
