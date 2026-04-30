from typing import List
from models.process import Process


def run_sjf(processes: List[Process]) -> dict:
    """
    Simulates the Shortest Job First (SJF) CPU scheduling algorithm (Non-preemptive).
    """
    # Sort initially by arrival time, then by pid to ensure stable tie-breaking
    processes = sorted(processes, key=lambda p: (p.arrival_time, p.pid))
    
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
            
        # Select the process with the shortest burst time
        # min() is stable, so tie-breakers are preserved from the initial sort
        shortest_process = min(available_processes, key=lambda p: p.burst_time)
        
        # Execute the process
        shortest_process.start_time = current_time
        shortest_process.completion_time = current_time + shortest_process.burst_time
        shortest_process.turnaround_time = shortest_process.completion_time - shortest_process.arrival_time
        shortest_process.waiting_time = shortest_process.turnaround_time - shortest_process.burst_time
        shortest_process.response_time = shortest_process.waiting_time  # For non-preemptive, response = waiting
        
        gantt_chart.append((shortest_process.pid, shortest_process.start_time, shortest_process.completion_time))
        
        current_time = shortest_process.completion_time
        is_completed[shortest_process.pid] = True
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
