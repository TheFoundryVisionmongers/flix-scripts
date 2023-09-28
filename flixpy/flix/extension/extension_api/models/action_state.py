from enum import Enum


class ActionState(str, Enum):
    COMPLETED = "completed"
    ERROR = "error"
    PROGRESS = "progress"
    STARTED = "started"

    def __str__(self) -> str:
        return str(self.value)
