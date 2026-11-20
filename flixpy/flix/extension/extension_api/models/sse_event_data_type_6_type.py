from enum import Enum


class SSEEventDataType6Type(str, Enum):
    PREFERENCES = "PREFERENCES"

    def __str__(self) -> str:
        return str(self.value)
