from enum import Enum


class ActionType(str, Enum):
    PANEL_ANNOTATE = "PANEL_ANNOTATE"
    PANEL_CREATE = "PANEL_CREATE"
    PANEL_UPDATE = "PANEL_UPDATE"

    def __str__(self) -> str:
        return str(self.value)
