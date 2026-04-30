from typing import List
from models.process import Process


def run_round_robin(processes: List[Process], time_quantum: int) -> dict:
    """
    Simulates the Round Robin CPU scheduling algorithm.
    """
    # Sort processes by arrival time to determine initial queue order
    processes = sorted(processes, key=lambda p: p.arrival_time)
    
    n = len(processes)
    remaining_burst = {p.pid: p.burst_time for p in processes}
    first_start = {p.pid: -1 for p in processes}
    
    current_time = 0
    completed = 0
    
    ready_queue = []
    in_queue_or_completed = set()
    
    # Check arrivals at time 0
    for p in processes:
        if p.arrival_time <= current_time:
            ready_queue.append(p)
            in_queue_or_completed.add(p.pid)
            
    gantt_chart = []
    
    while completed < n:
        if not ready_queue:
            # CPU is idle, jump to the next arrival time
            next_arrival = min(
                (p.arrival_time for p in processes if p.pid not in in_queue_or_completed),
                default=-1
            )
            if next_arrival != -1:
                current_time = next_arrival
                for p in processes:
                    if p.arrival_time <= current_time and p.pid not in in_queue_or_completed:
                        ready_queue.append(p)
                        in_queue_or_completed.add(p.pid)
            continue
            
        current_process = ready_queue.pop(0)
        
        # Record first start time for response time calculation
        if first_start[current_process.pid] == -1:
            first_start[current_process.pid] = current_time
            current_process.start_time = current_time
            current_process.response_time = current_time - current_process.arrival_time
            
        # Execute the process for the time quantum or remaining burst time
        execute_time = min(time_quantum, remaining_burst[current_process.pid])
        gantt_chart.append((current_process.pid, current_time, current_time + execute_time))
        
        current_time += execute_time
        remaining_burst[current_process.pid] -= execute_time
        
        # Check for new arrivals while this process was executing
        for p in processes:
            if p.arrival_time <= current_time and p.pid not in in_queue_or_completed:
                ready_queue.append(p)
                in_queue_or_completed.add(p.pid)
                
        # If the process isn't finished, put it back at the end of the ready queue
        if remaining_burst[current_process.pid] > 0:
            ready_queue.append(current_process)
        else:
            completed += 1
            current_process.completion_time = current_time
            current_process.turnaround_time = current_process.completion_time - current_process.arrival_time
            current_process.waiting_time = current_process.turnaround_time - current_process.burst_time

    # Sort again by pid for consistent output display
    processes = sorted(processes, key=lambda p: p.pid)

    avg_waiting = sum(p.waiting_time for p in processes) / n if n > 0 else 0
    avg_turnaround = sum(p.turnaround_time for p in processes) / n if n > 0 else 0
    avg_response = sum(p.response_time for p in processes) / n if n > 0 else 0

    return {
        "processes": processes,
        "gantt_chart": gantt_chart,
        "avg_waiting": avg_waiting,
        "avg_turnaround": avg_turnaround,
        "avg_response": avg_response,
        "time_quantum": time_quantum
    }
