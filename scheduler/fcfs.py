from models.process import Process


def run_fcfs(processes):
    # Sort by arrival time, then by pid to keep output consistent
    processes = sorted(processes, key=lambda p: (p.arrival_time, p.pid))

    current_time = 0
    gantt_chart = []

    for process in processes:
        # If CPU is idle, jump to the next process arrival
        if current_time < process.arrival_time:
            current_time = process.arrival_time

        process.start_time = current_time
        process.completion_time = process.start_time + process.burst_time
        process.waiting_time = process.start_time - process.arrival_time
        process.turnaround_time = process.completion_time - process.arrival_time
        process.response_time = process.waiting_time

        gantt_chart.append((process.pid, process.start_time, process.completion_time))

        current_time = process.completion_time

    avg_waiting = sum(p.waiting_time for p in processes) / len(processes)
    avg_turnaround = sum(p.turnaround_time for p in processes) / len(processes)
    avg_response = sum(p.response_time for p in processes) / len(processes)

    return {
        "processes": processes,
        "gantt_chart": gantt_chart,
        "avg_waiting": avg_waiting,
        "avg_turnaround": avg_turnaround,
        "avg_response": avg_response,
    }