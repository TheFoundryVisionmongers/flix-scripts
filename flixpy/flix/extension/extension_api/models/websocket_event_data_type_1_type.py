from enum import Enum


class WebsocketEventDataType1Type(str, Enum):
    PROJECT = "PROJECT"

    def __str__(self) -> str:
        return str(self.value)
