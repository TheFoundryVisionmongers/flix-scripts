from enum import Enum


class WebsocketEventDataType3Type(str, Enum):
    OPEN = "OPEN"

    def __str__(self) -> str:
        return str(self.value)
