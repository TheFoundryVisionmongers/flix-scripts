from enum import Enum


class ClientEventType(str, Enum):
    ACTION = "ACTION"
    OPEN = "OPEN"
    PING = "PING"
    PROJECT = "PROJECT"
    STATUS = "STATUS"
    VERSION = "VERSION"

    def __str__(self) -> str:
        return str(self.value)
