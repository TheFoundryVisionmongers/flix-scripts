from enum import Enum


class SourceFilePreviewMode(str, Enum):
    FIRST_PANEL = "first_panel"
    SOURCE_FILE = "source_file"

    def __str__(self) -> str:
        return str(self.value)
