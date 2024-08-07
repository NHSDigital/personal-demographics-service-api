import json
import requests

from typing import Optional, Dict, Any, Generator


def find_item_in_dict(obj={}, search_key=""):
    """
    Recursively searches through a dictionary for the key provided and returns its value
    Args:
        obj (dict): the object to search through
        key (string): the key to find
    """
    found_items = [item for item in find_items_in_dict(obj, search_key)]
    return found_items[0] if found_items else None


def find_items_in_dict(obj: dict, key: Any) -> Generator[Any, None, None]:
    if hasattr(obj, 'items'):
        for k, v in obj.items():
            if k == key:
                yield v
            if isinstance(v, dict):
                for value in find_items_in_dict(v, key):
                    yield value
            elif isinstance(v, list):
                for el in v:
                    for value in find_items_in_dict(el, key):
                        yield value


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


def get_role_id_from_user_info_endpoint(token, identity_service_base_url) -> str:

    url = f'{identity_service_base_url}/userinfo'
    headers = {"Authorization": f"Bearer {token}"}

    user_info_resp = requests.get(url, headers=headers)
    user_info = json.loads(user_info_resp.text)

    assert user_info_resp.status_code == 200
    return user_info['nhsid_nrbac_roles'][0]['person_roleid']
