from enum import Enum


class SourceFileType(str, Enum):
    EDITORIAL = "Editorial"
    SCRIPT = "Script"
    SKETCH = "Sketch"
    STANDALONE = "Standalone"
    THREE_D = "3D"

    def __str__(self) -> str:
        return str(self.value)
