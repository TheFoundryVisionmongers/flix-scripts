from enum import Enum


class WebsocketEventDataType2Type(str, Enum):
    OPEN = "OPEN"

    def __str__(self) -> str:
        return str(self.value)
