from enum import Enum


class ActionRegistrationResponseType(str, Enum):
    PANEL_BROWSER_ACTION = "PanelBrowserAction"

    def __str__(self) -> str:
        return str(self.value)
