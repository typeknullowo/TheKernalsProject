from typing import List, Optional
from models.process import Process, ProcessState

class SimulationEngine:
    def __init__(self, processes: List[Process], algorithm: str, time_quantum: int = 2):
        self.algorithm = algorithm
        self.time_quantum = time_quantum
        
        # Keep a deep copy or use provided processes directly. Assuming they are fresh.
        # Sort unarrived processes by arrival time.
        self.unarrived = sorted(processes, key=lambda p: p.arrival_time)
        self.ready_queue: List[Process] = []
        self.running: Optional[Process] = None
        self.terminated: List[Process] = []
        
        self.time = 0
        self.quantum_elapsed = 0
        self.context_switches = 0
        self.last_running_pid = None
        self.gantt_chart = []
        self.event_log = []
        
        # Ensure states are initialized
        for p in self.unarrived:
            p.set_state(ProcessState.NEW)
            p.remaining_time = p.burst_time
            p.start_time = -1
            p.response_time = -1

    def is_finished(self) -> bool:
        return len(self.unarrived) == 0 and len(self.ready_queue) == 0 and self.running is None

    def tick(self) -> dict:
        """
        Advances the simulation by 1 time unit.
        Returns the state snapshot.
        """
        if self.is_finished():
            return self.get_state()

        # 1. Check for arriving processes
        arrived_this_tick = []
        while self.unarrived and self.unarrived[0].arrival_time == self.time:
            p = self.unarrived.pop(0)
            p.set_state(ProcessState.READY)
            self.ready_queue.append(p)
            arrived_this_tick.append(p)
            self.log(f"[{self.time}] Process {p.pid} arrived and added to ready queue.")

        # 2. Handle currently running process completion or preemption
        if self.running:
            self.running.remaining_time -= 1
            self.quantum_elapsed += 1
            
            # Check if finished
            if self.running.remaining_time == 0:
                self.running.completion_time = self.time + 1
                self.running.turnaround_time = self.running.completion_time - self.running.arrival_time
                self.running.waiting_time = self.running.turnaround_time - self.running.burst_time
                self.running.set_state(ProcessState.TERMINATED)
                self.terminated.append(self.running)
                self.update_gantt(self.running.pid, self.time + 1)
                self.log(f"[{self.time + 1}] Process {self.running.pid} terminated.")
                self.last_running_pid = self.running.pid
                self.running = None
                self.quantum_elapsed = 0
            
            # Check for preemption (Round Robin)
            elif self.algorithm == "Round Robin" and self.quantum_elapsed >= self.time_quantum:
                self.running.set_state(ProcessState.READY)
                self.ready_queue.append(self.running)
                self.update_gantt(self.running.pid, self.time + 1)
                self.log(f"[{self.time + 1}] Process {self.running.pid} preempted (quantum expired).")
                self.last_running_pid = self.running.pid
                self.running = None
                self.quantum_elapsed = 0
            else:
                self.update_gantt(self.running.pid, self.time + 1)

        # 3. Schedule next process if CPU is idle
        if self.running is None and self.ready_queue:
            if self.algorithm == "FCFS" or self.algorithm == "Round Robin":
                # Both use FIFO ready queue for selection
                self.running = self.ready_queue.pop(0)
            elif self.algorithm == "SJF":
                # Sort by shortest burst time
                self.ready_queue.sort(key=lambda p: (p.burst_time, p.arrival_time))
                self.running = self.ready_queue.pop(0)
            elif self.algorithm == "Priority":
                # Sort by priority (lower number = higher priority)
                self.ready_queue.sort(key=lambda p: (p.priority, p.arrival_time))
                self.running = self.ready_queue.pop(0)
            
            # Context switch logic
            if self.last_running_pid is not None and self.last_running_pid != self.running.pid:
                self.context_switches += 1
                self.log(f"[{self.time}] Context Switch: {self.last_running_pid} -> {self.running.pid}")
                
            self.running.set_state(ProcessState.RUNNING)
            
            if self.running.start_time == -1:
                self.running.start_time = self.time
                self.running.response_time = self.running.start_time - self.running.arrival_time
                
            self.log(f"[{self.time}] Process {self.running.pid} started executing on CPU.")
            self.update_gantt(self.running.pid, self.time, start_new=True)

        self.time += 1
        return self.get_state()

    def update_gantt(self, pid: str, current_time: int, start_new: bool = False):
        if not self.gantt_chart or start_new:
            # First entry or forced new block
            if self.gantt_chart and self.gantt_chart[-1]['pid'] == pid:
                 self.gantt_chart[-1]['end'] = current_time
            else:
                self.gantt_chart.append({"pid": pid, "start": current_time if start_new else current_time-1, "end": current_time})
        else:
            last = self.gantt_chart[-1]
            if last["pid"] == pid:
                last["end"] = current_time
            else:
                self.gantt_chart.append({"pid": pid, "start": current_time - 1, "end": current_time})

    def log(self, message: str):
        self.event_log.append(message)

    def get_state(self) -> dict:
        # Calculate averages
        avg_wait = 0
        avg_turnaround = 0
        avg_response = 0
        if self.terminated:
            avg_wait = sum(p.waiting_time for p in self.terminated) / len(self.terminated)
            avg_turnaround = sum(p.turnaround_time for p in self.terminated) / len(self.terminated)
            avg_response = sum(p.response_time for p in self.terminated if p.response_time != -1) / len(self.terminated)

        return {
            "time": self.time,
            "algorithm": self.algorithm,
            "unarrived": list(self.unarrived),
            "ready_queue": list(self.ready_queue),
            "running": self.running,
            "terminated": list(self.terminated),
            "gantt_chart": list(self.gantt_chart),
            "event_log": list(self.event_log),
            "context_switches": self.context_switches,
            "avg_wait": avg_wait,
            "avg_turnaround": avg_turnaround,
            "avg_response": avg_response
        }
