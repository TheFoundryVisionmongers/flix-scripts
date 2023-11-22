from enum import Enum


class WebsocketEventDataType4Type(str, Enum):
    VERSION = "VERSION"

    def __str__(self) -> str:
        return str(self.value)
