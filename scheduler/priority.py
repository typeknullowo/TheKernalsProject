from typing import List
from models.process import Process


def run_priority(processes: List[Process]) -> dict:
    """
    Simulates the Priority CPU scheduling algorithm (Non-preemptive).
    Assumes a lower priority number means a higher priority.
    """
    # Sort initially by arrival time, then by priority, then by pid
    processes = sorted(processes, key=lambda p: (p.arrival_time, p.priority, p.pid))
    
    n = len(processes)
    current_time = 0
    completed = 0
    gantt_chart = []
    
    # Track completed processes
    is_completed = {p.pid: False for p in processes}
    
    while completed < n:
        # Find all available processes at current_time
        available_processes = [
            p for p in processes if p.arrival_time <= current_time and not is_completed[p.pid]
        ]
        
        if not available_processes:
            # CPU is idle, jump to the next arrival time
            next_arrival = min(
                p.arrival_time for p in processes if not is_completed[p.pid]
            )
            current_time = next_arrival
            continue
            
        # Select the process with the highest priority (lowest priority number)
        # min() is stable, so tie-breakers are preserved
        highest_priority_process = min(available_processes, key=lambda p: p.priority)
        
        # Execute the process
        highest_priority_process.start_time = current_time
        highest_priority_process.completion_time = current_time + highest_priority_process.burst_time
        highest_priority_process.turnaround_time = highest_priority_process.completion_time - highest_priority_process.arrival_time
        highest_priority_process.waiting_time = highest_priority_process.turnaround_time - highest_priority_process.burst_time
        highest_priority_process.response_time = highest_priority_process.waiting_time  # non-preemptive
        
        gantt_chart.append((highest_priority_process.pid, highest_priority_process.start_time, highest_priority_process.completion_time))
        
        current_time = highest_priority_process.completion_time
        is_completed[highest_priority_process.pid] = True
        completed += 1
        
    avg_waiting = sum(p.waiting_time for p in processes) / n if n > 0 else 0
    avg_turnaround = sum(p.turnaround_time for p in processes) / n if n > 0 else 0
    avg_response = sum(p.response_time for p in processes) / n if n > 0 else 0

    return {
        "processes": processes,
        "gantt_chart": gantt_chart,
        "avg_waiting": avg_waiting,
        "avg_turnaround": avg_turnaround,
        "avg_response": avg_response,
    }
