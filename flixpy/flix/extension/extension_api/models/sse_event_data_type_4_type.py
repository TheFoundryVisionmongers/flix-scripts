from enum import Enum


class SSEEventDataType4Type(str, Enum):
    OPEN = "OPEN"

    def __str__(self) -> str:
        return str(self.value)
