from dataclasses import dataclass

from .ApigeeAppCustomAttributes import ApigeeAppCustomAttributes


@dataclass
class ApigeeApp:
    id: str
    requested_custom_attributes: ApigeeAppCustomAttributes

    def __str__(self):
        return f"###\nApp ID: {self.id}\nCustom attributes: {str(self.requested_custom_attributes)}\n###\n"
