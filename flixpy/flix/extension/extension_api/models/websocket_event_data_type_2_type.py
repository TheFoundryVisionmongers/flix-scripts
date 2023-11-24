from enum import Enum


class WebsocketEventDataType2Type(str, Enum):
    STATUS = "STATUS"

    def __str__(self) -> str:
        return str(self.value)
