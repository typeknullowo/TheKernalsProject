from dataclasses import dataclass
from enum import Enum


class ThreadState(Enum):
    NEW = "New"
    READY = "Ready"
    RUNNING = "Running"
    WAITING = "Waiting"
    TERMINATED = "Terminated"


@dataclass
class ThreadModel:
    tid: str
    parent_pid: str
    state: ThreadState = ThreadState.NEW

    def set_state(self, new_state: ThreadState):
        self.state = new_state
