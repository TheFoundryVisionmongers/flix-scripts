from enum import Enum


class WebsocketEventDataType7Type(str, Enum):
    PANEL_METADATA_UPDATE = "PANEL_METADATA_UPDATE"

    def __str__(self) -> str:
        return str(self.value)
