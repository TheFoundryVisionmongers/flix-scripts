from enum import Enum


class WebsocketEventDataType2Type(str, Enum):
    PROJECT = "PROJECT"

    def __str__(self) -> str:
        return str(self.value)
