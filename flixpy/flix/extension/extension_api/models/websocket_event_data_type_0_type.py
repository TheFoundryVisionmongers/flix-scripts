from enum import Enum


class WebsocketEventDataType0Type(str, Enum):
    ACTION = "ACTION"

    def __str__(self) -> str:
        return str(self.value)
