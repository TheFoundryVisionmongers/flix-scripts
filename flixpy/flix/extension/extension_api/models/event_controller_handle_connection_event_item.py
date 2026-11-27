from enum import Enum


class EventControllerHandleConnectionEventItem(str, Enum):
    ACTION = "action"
    OPEN = "open"
    PANEL_METADATA_UPDATE = "panel_metadata_update"
    PING = "ping"
    PREFERENCES = "preferences"
    PROJECT = "project"
    PROJECT_METADATA_UPDATE = "project_metadata_update"
    STATUS = "status"
    VERSION = "version"

    def __str__(self) -> str:
        return str(self.value)
