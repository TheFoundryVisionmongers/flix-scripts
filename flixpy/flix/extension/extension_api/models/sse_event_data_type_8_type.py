from enum import Enum


class SSEEventDataType8Type(str, Enum):
    PROJECT_METADATA_UPDATE = "PROJECT_METADATA_UPDATE"

    def __str__(self) -> str:
        return str(self.value)
