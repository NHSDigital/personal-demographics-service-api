from typing import Dict


class UserDirectory:
    healthcare_worker = {
        "level": "aal3",
        "login_form": {"username": "656005750104"},
    }

    P9 = {
        "login_form": {"username": "9912003071"},
    }

    P9_WITH_RELATED_PERSON  = {
            "level": "P9",
            "login_form": {"username": "9472063845"},
    }

    P5 = {
        "login_form": {"username": "9912003071"},
    }

    p5 = {
        "level": "p5",
        "login_form": {"username": "9912003071"},
    }

    P0 = {
        "login_form": {"username": "9912003071"},
    }

    def __getitem__(self, key: str) -> Dict[str, str]:
        user = getattr(self, key)

        auth_details = {}
        self.set_api_name(user, key, auth_details)
        self.set_access(user, key, auth_details)
        self.set_level(user, key, auth_details)
        self.set_login_form(user, key, auth_details)
        self.set_force_new_token(user, key, auth_details)

        return auth_details

    def set_api_name(self, user: dict, key: str, auth_details: Dict[str, str]) -> None:
        api_name = user.get('api_name')
        auth_details['api_name'] = api_name if api_name else 'personal-demographics-service'

    def set_access(self, user: dict, key: str, auth_details: Dict[str, str]) -> None:
        access = user.get('access')
        if access:
            auth_details['access'] = access
        elif key.lower().startswith('p'):
            auth_details['access'] = 'patient'
        else:
            auth_details['access'] = key

    def set_level(self, user: dict, key: str, auth_details: Dict[str, str]) -> None:
        level = user.get('level')
        auth_details['level'] = level if level else key

    def set_login_form(self, user: dict, key: str, auth_details: Dict[str, str]) -> None:
        login_form = user.get('login_form')
        if login_form:
            auth_details['login_form'] = login_form

    def set_force_new_token(self, user: dict, key: str, auth_details: Dict[str, str]) -> None:
        force_new_token = user.get('force_new_token')
        auth_details['force_new_token'] = force_new_token if force_new_token else True
