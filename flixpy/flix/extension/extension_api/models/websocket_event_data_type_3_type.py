from enum import Enum


class WebsocketEventDataType3Type(str, Enum):
    PING = "PING"

    def __str__(self) -> str:
        return str(self.value)
