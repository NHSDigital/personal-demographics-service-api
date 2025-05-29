from dataclasses import dataclass
from typing import Union


@dataclass
class ApigeeApp:
    id: str
    requested_flow_vars: Union[dict, None]

    def __str__(self):
        return f'App ID: {self.id} Requested APIM flow var key/values: {self.requested_flow_vars}'
