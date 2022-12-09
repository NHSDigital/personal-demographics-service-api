from typing import Optional, Dict
import random
import string


def find_item_in_dict(obj={}, search_key=""):
    """
    Recursively searches through a dictionary for the key provided and returns its value
    Args:
        obj (dict): the object to search through
        key (string): the key to find
    """
    if search_key in obj:
        return obj[search_key]

    for key, val in obj.items():
        if isinstance(val, dict):
            item = find_item_in_dict(val, search_key)
            if item is not None:
                return item


def get_proxy_name(base_path, environment):
    if "-pr-" in base_path:
        return base_path.replace("/FHIR/R4", "")

    return f'{base_path.replace("/FHIR/R4", "")}-{environment}'


def generate_random_email_address():
    letters = string.ascii_lowercase
    random_letters = "".join(random.choice(letters) for i in range(10))
    return f"random.{random_letters}@test.com"


def get_add_telecom_email_patch_body():
    return {
        "patches": [
            {
                "op": "add",
                "path": "/telecom/-",
                "value": {
                    "period": {"start": "2020-02-27"},
                    "system": "email",
                    "use": "work",
                    "value": "test@test.com",
                },
            }
        ]
    }


def add_auth_header(headers: Dict[str, str], auth: Optional[Dict[str, str]]):
    """
    Add the authorization header to the headers dict.

    If `auth` is empty, then do not add the header at all.
    """
    if not auth:
        return headers

    access_token = auth["access_token"] or ""
    token_type = auth.get("token_type", "Bearer")

    if access_token == "" and token_type == "":
        headers["Authorization"] = ""
    else:
        headers["Authorization"] = f"{token_type} {access_token}"

    return headers
