import requests
import json
import urllib.parse as urlparse
from common.auth import Auth
from urllib.parse import parse_qs
from locust import HttpUser, task, between

class PersonalDemographicsUser(HttpUser):
    wait_time = between(5, 9)

    def on_start(self):
        authenticator = Auth()
        self.credentials = authenticator.login()
        self.headers = { 
            "Authorization": self.credentials["token_type"] + " " + self.credentials["access_token"],
            "NHSD-Identity-UUID": "1234567890",
            "NHSD-Session-URID": "1234567890",
        }

    @task(1)
    def pds_api(self):
        self.client.get("/personal-demographics/Patient/5900018512", headers=self.headers)

