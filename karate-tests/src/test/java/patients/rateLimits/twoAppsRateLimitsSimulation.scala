package patients

import com.intuit.karate.gatling.PreDef._
import io.gatling.core.Predef._
import scala.concurrent.duration._


class GetPatientByTwoAppsSimulation extends Simulation {
 // === Configuration ===
  val rateLimitAppRequests = Integer.getInteger("rateLimitAppRequests")
  val proxyRateLimit = Integer.getInteger("proxyRateLimitAppRequests")
  val duration = Integer.getInteger("duration")
  val protocol = karateProtocol()
  protocol.runner.karateEnv("veit07")

  // === State Tracking ===
  var app1Counter = 0
  var app2Counter = 0
  var app1_429s, app2_429s = Seq[Int]()
  var app1_429Timestamps, app2_429Timestamps = Seq[String]()

  // === Helper to Handle 429 Tracking ===
  def track429(session: Session, appLabel: String): Session = {
    if (session.contains("is429") && session("is429").as[Boolean]) {
      val index = session("requestIndex").as[Int]
      val timestamp = session("timestamp429").as[String]
      val entry = s"Request $index at $timestamp"

      appLabel match {
        case "App1" =>
          app1_429s = app1_429s :+ index
          app1_429Timestamps = app1_429Timestamps :+ entry
        case "App2" =>
          app2_429s = app2_429s :+ index
          app2_429Timestamps = app2_429Timestamps :+ entry
      }
    }
    session
  }

  // === Scenario Definitions ===
  def scenarioForApp(appLabel: String, requestingApp: String) = {
    scenario(s"${appLabel}Test")
      .exec(session => {
        val index = appLabel match {
          case "App1" => app1Counter += 1; app1Counter
          case "App2" => app2Counter += 1; app2Counter
        }
        session
          .set("requestIndex", index)
          .set("appName", appLabel)
      })
      .exec(karateSet("requestingApp", session => requestingApp))
      // Optional: Log each request for debugging
      .exec(session => {
        val app = session("appName").as[String]
        val idx = session("requestIndex").as[Int]
        val now = java.time.Instant.now.toString
        println(s"[DEBUG] $app - Request $idx at $now")
        session
      })
      .exec(karateFeature("classpath:patients/rateLimits/getPatientDetails.feature"))
      .exec(session => track429(session, appLabel))
  }

  val rateLimitingAppScenario = scenarioForApp("App1", "rateLimitingApp")
  val proxyRateLimitingAppScenario = scenarioForApp("App2", "proxyRateLimitingApp")

  // === Simulation Setup ===
  setUp(
    rateLimitingAppScenario.inject(rampUsers(rateLimitAppRequests) during (duration.seconds)).protocols(protocol).andThen(
      proxyRateLimitingAppScenario.inject(rampUsers(proxyRateLimit) during (duration.seconds)).protocols(protocol)
    )
  )

  // === Report Output ===
  after {
    println("=== Simulation Complete ===")
    println(s"Total requests from App1Test: $rateLimitAppRequests")
    println(s"Total requests from App2Test: $proxyRateLimit")

    def print429s(appLabel: String, count: Int, timestamps: Seq[String]) = {
      println(s"Total 429 responses from $appLabel: $count")
      if (timestamps.nonEmpty) timestamps.foreach(println)
      else println("No 429 responses received")
    }

    print429s("App1Test", app1_429s.size, app1_429Timestamps)
    print429s("App2Test", app2_429s.size, app2_429Timestamps)
  }
}
