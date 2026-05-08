from enum import Enum


class SSEEventDataType2Type(str, Enum):
    PROJECT = "PROJECT"

    def __str__(self) -> str:
        return str(self.value)
