from enum import Enum


class SSEEventDataType5Type(str, Enum):
    VERSION = "VERSION"

    def __str__(self) -> str:
        return str(self.value)
