from enum import Enum


class SSEEventDataType3Type(str, Enum):
    ACTION = "ACTION"

    def __str__(self) -> str:
        return str(self.value)
