from enum import Enum


class ClientEventType(str, Enum):
    ACTION = "ACTION"
    OPEN = "OPEN"
    PANEL_METADATA_UPDATE = "PANEL_METADATA_UPDATE"
    PING = "PING"
    PREFERENCES = "PREFERENCES"
    PROJECT = "PROJECT"
    PROJECT_METADATA_UPDATE = "PROJECT_METADATA_UPDATE"
    STATUS = "STATUS"
    VERSION = "VERSION"

    def __str__(self) -> str:
        return str(self.value)
