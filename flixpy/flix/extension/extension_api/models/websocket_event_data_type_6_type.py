from enum import Enum


class WebsocketEventDataType6Type(str, Enum):
    PREFERENCES = "PREFERENCES"

    def __str__(self) -> str:
        return str(self.value)
