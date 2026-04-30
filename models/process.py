from dataclasses import dataclass, field
from enum import Enum
from typing import List


class ProcessState(Enum):
    NEW = "New"
    READY = "Ready"
    RUNNING = "Running"
    WAITING = "Waiting"
    TERMINATED = "Terminated"


@dataclass
class Process:
    pid: str
    arrival_time: int
    burst_time: int

    priority: int = 0
    start_time: int = -1
    completion_time: int = 0
    waiting_time: int = 0
    turnaround_time: int = 0
    response_time: int = -1
    state: ProcessState = ProcessState.NEW
    remaining_time: int = 0
    threads: List['ThreadModel'] = field(default_factory=list)

    def __post_init__(self):
        self.remaining_time = self.burst_time

    def set_state(self, new_state: ProcessState):
        self.state = new_state