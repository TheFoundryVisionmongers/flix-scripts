from enum import Enum


class EventControllerHandleConnectionEventItem(str, Enum):
    ACTION = "action"
    CUSTOM = "custom"
    OPEN = "open"
    PING = "ping"
    PREFERENCES = "preferences"
    PROJECT = "project"
    STATUS = "status"
    VERSION = "version"

    def __str__(self) -> str:
        return str(self.value)
