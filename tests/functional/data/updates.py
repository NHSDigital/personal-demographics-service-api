from dataclasses import dataclass
from ..configuration.config import TEST_PATIENT_ID
import re
from typing import Union


@dataclass
class Update:
    nhs_number: str
    operation: str = 'replace'
    path: str = 'gender'
    record: dict = None
    value: Union[str, dict] = None
    etag: str = None

    @property
    def patches(self) -> dict:
        patch = {
            "op": self.operation,
            "path": f'/{self.path}',
            "value": self.value
        }
        return {"patches": [patch]}

    @property
    def record_version(self) -> str:
        return re.findall(r'\d+', self.etag)[0]


DEFAULT = Update(nhs_number=TEST_PATIENT_ID)
SELF = Update(nhs_number='9912003071',
              path='telecom/0')
