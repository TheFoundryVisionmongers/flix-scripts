from enum import Enum


class EventType(str, Enum):
    ACTION = "ACTION"
    OPEN = "OPEN"
    PING = "PING"
    PROJECT = "PROJECT"
    PUBLISH = "PUBLISH"
    STATUS = "STATUS"
    VERSION = "VERSION"

    def __str__(self) -> str:
        return str(self.value)
