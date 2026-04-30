def generate_dashboard(scheduler_results: dict, paging_results: list, deadlock_safe: bool):
    print("\n" + "="*80)
    print(" " * 25 + "OS ARENA ANALYTICS DASHBOARD")
    print("="*80)
    
    print("\n--- CPU Scheduling Comparison ---")
    print(f"{'Algorithm':<15} | {'Avg Wait':<10} | {'Avg Turnaround':<15} | {'Avg Response':<15} | {'Context Switches'}")
    print("-" * 80)
    for name, res in scheduler_results.items():
        avg_w = f"{res['avg_waiting']:.2f}"
        avg_t = f"{res['avg_turnaround']:.2f}"
        avg_r = f"{res['avg_response']:.2f}"
        # Simple context switch estimation: entries in Gantt chart minus 1
        cs = len(res['gantt_chart']) - 1 if len(res['gantt_chart']) > 0 else 0
        print(f"{name:<15} | {avg_w:<10} | {avg_t:<15} | {avg_r:<15} | {cs}")
        
    print("\n--- Virtual Memory Statistics ---")
    print(f"{'Algorithm':<15} | {'Page Hits':<10} | {'Page Faults':<12} | {'Fault Rate'}")
    print("-" * 80)
    for res in paging_results:
        alg = res['algorithm']
        hits = res['hits']
        faults = res['faults']
        rate = (faults / (hits + faults)) * 100 if (hits + faults) > 0 else 0
        print(f"{alg:<15} | {hits:<10} | {faults:<12} | {rate:.2f}%")
        
    print("\n--- System Safety ---")
    state_str = "SAFE" if deadlock_safe else "UNSAFE (Deadlock Risk Detected)"
    print(f"Banker's Algorithm State: {state_str}")
    print("=" * 80 + "\n")
