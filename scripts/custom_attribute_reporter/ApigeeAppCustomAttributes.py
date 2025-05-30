from dataclasses import dataclass
from typing import Union


@dataclass
class ApigeeAppCustomAttributes:
    requested_flow_vars: Union[dict, None]
    rate_limit: Union[dict, None]

    def __str__(self):
        return f"Requested APIM flow var key/values: {self.requested_flow_vars}\nRate limit: {self.rate_limit}"
