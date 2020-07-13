import requests
import json
import urllib.parse as urlparse
from authenticator import Authenticator
from urllib.parse import parse_qs
from locust import HttpUser, task, between

class PersonalDemographicsUser(HttpUser):
    wait_time = between(5, 9)

    def on_start(self):
        authenticator = Authenticator()
        self.credentials = authenticator.login()

    @task(1)
    def pds_api(self):
        self.client.get("/personal-demographics")

