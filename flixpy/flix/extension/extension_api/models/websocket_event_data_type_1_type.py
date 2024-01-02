from enum import Enum


class WebsocketEventDataType1Type(str, Enum):
    STATUS = "STATUS"

    def __str__(self) -> str:
        return str(self.value)
