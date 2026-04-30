from scheduler.fcfs import run_fcfs
from scheduler.round_robin import run_round_robin
from scheduler.sjf import run_sjf
from scheduler.priority import run_priority
from tests.sample_scenarios import get_sample_processes
from models.process import ProcessState, Process
from models.thread_model import ThreadModel, ThreadState
from sync.mutex_demo import run_sync_demo
from sync.banker import run_bankers_demo, BankersAlgorithm
from memory.allocation import run_memory_demo
from memory.paging import run_paging_demo, run_fifo, run_lru, run_optimal, print_paging_result
from ui.dashboard import generate_dashboard
import time


def print_results(result: dict, title: str) -> None:
    print(f"\n{title}")
    print("-" * 80)
    print(
        f"{'PID':<8}{'Arrival':<10}{'Burst':<8}{'Priority':<10}"
        f"{'Start':<8}{'Complete':<10}{'Waiting':<10}{'Turnaround':<12}"
    )
    print("-" * 80)

    for p in result["processes"]:
        print(
            f"{p.pid:<8}{p.arrival_time:<10}{p.burst_time:<8}{p.priority:<10}"
            f"{p.start_time:<8}{p.completion_time:<10}"
            f"{p.waiting_time:<10}{p.turnaround_time:<12}"
        )

    print("-" * 80)
    print(f"Average Waiting Time: {result['avg_waiting']:.2f}")
    print(f"Average Turnaround Time: {result['avg_turnaround']:.2f}")
    print(f"Average Response Time: {result['avg_response']:.2f}")

    print("\nGantt Chart:")
    gantt_output = ""
    for pid, start, end in result["gantt_chart"]:
        gantt_output += f"| {pid} ({start}-{end}) "
    gantt_output += "|"
    print(gantt_output)


def run_state_demo():
    print("\nProcess and Thread State Visualization Demo")
    print("-" * 80)
    p = Process("P_DEMO", arrival_time=0, burst_time=10)
    print(f"[{p.pid}] Created -> State: {p.state.value}")
    t1 = ThreadModel("T1", parent_pid=p.pid)
    t2 = ThreadModel("T2", parent_pid=p.pid)
    p.threads.extend([t1, t2])
    print(f"[{p.pid}] Added Threads: {t1.tid} (State: {t1.state.value}), {t2.tid} (State: {t2.state.value})")
    p.set_state(ProcessState.READY)
    t1.set_state(ThreadState.READY)
    t2.set_state(ThreadState.READY)
    print(f"[{p.pid}] Scheduled -> State: {p.state.value}")
    p.set_state(ProcessState.RUNNING)
    t1.set_state(ThreadState.RUNNING)
    print(f"[{p.pid}] Executing -> State: {p.state.value} | {t1.tid} is {t1.state.value}, {t2.tid} is {t2.state.value}")
    p.set_state(ProcessState.WAITING)
    t1.set_state(ThreadState.WAITING)
    print(f"[{p.pid}] I/O Request -> State: {p.state.value} | {t1.tid} is {t1.state.value}")
    p.set_state(ProcessState.TERMINATED)
    t1.set_state(ThreadState.TERMINATED)
    t2.set_state(ThreadState.TERMINATED)
    print(f"[{p.pid}] Completed -> State: {p.state.value} | Threads terminated.")
    print("-" * 80)


def run_heavy_cpu_demo():
    print("\n" + "="*80)
    print(" PRESET SCENARIO: HEAVY CPU")
    print(" Demonstrating Round Robin behavior under extreme burst times.")
    print("="*80)
    
    heavy_procs = [
        Process("P1", arrival_time=0, burst_time=80, priority=1),
        Process("P2", arrival_time=2, burst_time=150, priority=2),
        Process("P3", arrival_time=5, burst_time=60, priority=3),
    ]
    
    # We use a large time quantum so it doesn't flood the Gantt chart completely, 
    # but still shows context switching
    rr_result = run_round_robin(heavy_procs, time_quantum=40)
    print_results(rr_result, "Round Robin (Time Quantum = 40) - Heavy CPU Load")


def run_deadlock_prone_demo():
    print("\n" + "="*80)
    print(" PRESET SCENARIO: DEADLOCK PRONE")
    print(" Simulating a Banker's Algorithm state that is immediately UNSAFE.")
    print("="*80)
    
    processes = ["P0", "P1", "P2"]
    available = [1, 0, 0] # Barely any resources left
    max_claim = [[4, 3, 1], [2, 1, 4], [1, 3, 3]]
    allocation = [[2, 0, 0], [1, 1, 0], [0, 2, 1]]
    
    banker = BankersAlgorithm(processes, available, max_claim, allocation)
    banker.print_state()
    is_safe, seq = banker.is_safe_state()
    
    if is_safe:
        print(f"\nState is SAFE. Sequence: {' -> '.join(seq)}")
    else:
        print("\n!!! Initial State is UNSAFE (Deadlock Highly Probable) !!!")
        print("Banker's algorithm confirms no safe sequence exists to satisfy all processes.")


def run_heavy_memory_demo():
    print("\n" + "="*80)
    print(" PRESET SCENARIO: HEAVY MEMORY (PAGE FAULT STORM)")
    print(" Demonstrating page replacement with very few frames and high locality misses.")
    print("="*80)
    
    # Extremely fragmented and repetitive string that exceeds frame capacity frequently
    reference_string = [1, 2, 3, 4, 5, 1, 2, 3, 4, 5, 1, 2, 3, 4, 5]
    num_frames = 3 # Too small to hold the working set
    
    print(f"Reference String: {reference_string}")
    print(f"Number of Frames: {num_frames} (Thrashing Expected)")
    
    fifo_result = run_fifo(reference_string, num_frames)
    print_paging_result(fifo_result)


def run_everything():
    fcfs_result = run_fcfs(get_sample_processes())
    print_results(fcfs_result, "FCFS Scheduling Results")

    rr_result = run_round_robin(get_sample_processes(), time_quantum=2)
    print_results(rr_result, "Round Robin Scheduling Results (Time Quantum = 2)")

    sjf_result = run_sjf(get_sample_processes())
    print_results(sjf_result, "SJF Scheduling Results (Non-preemptive)")

    priority_result = run_priority(get_sample_processes())
    print_results(priority_result, "Priority Scheduling Results (Non-preemptive)")

    run_state_demo()
    run_sync_demo()
    
    is_safe = run_bankers_demo()
    run_memory_demo()
    paging_results = run_paging_demo()

    scheduler_results = {
        "FCFS": fcfs_result,
        "Round Robin": rr_result,
        "SJF": sjf_result,
        "Priority": priority_result
    }
    generate_dashboard(scheduler_results, paging_results, is_safe)


def interactive_menu():
    while True:
        print("\n" + "="*50)
        print(" OS ARENA - INTERACTIVE MENU")
        print("="*50)
        print("1. Run 'Heavy CPU' Scenario")
        print("2. Run 'Deadlock-Prone' Scenario")
        print("3. Run 'Heavy Memory' Scenario")
        print("4. Run Everything (Standard Demo & Dashboard)")
        print("5. Exit")
        
        choice = input("Select an option (1-5): ").strip()
        
        if choice == '1':
            run_heavy_cpu_demo()
        elif choice == '2':
            run_deadlock_prone_demo()
        elif choice == '3':
            run_heavy_memory_demo()
        elif choice == '4':
            run_everything()
        elif choice == '5':
            print("Exiting OS Arena... Goodbye!")
            break
        else:
            print("Invalid choice. Please select 1-5.")


import sys
from PyQt5.QtWidgets import QApplication

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        interactive_menu()
    else:
        # Avoid circular imports by importing GUI right before we use it
        from ui.main_window import OSArenaGUI
        app = QApplication(sys.argv)
        gui = OSArenaGUI()
        gui.show()
        sys.exit(app.exec_())