from typing import List, Tuple

class BankersAlgorithm:
    def __init__(self, processes: List[str], available: List[int], max_claim: List[List[int]], allocation: List[List[int]]):
        self.processes = processes
        self.available = available
        self.max_claim = max_claim
        self.allocation = allocation
        
        self.num_processes = len(processes)
        self.num_resources = len(available)
        
        # Calculate the Need matrix: Need[i][j] = Max[i][j] - Allocation[i][j]
        self.need = []
        for i in range(self.num_processes):
            process_need = []
            for j in range(self.num_resources):
                process_need.append(self.max_claim[i][j] - self.allocation[i][j])
            self.need.append(process_need)

    def is_safe_state(self) -> Tuple[bool, List[str]]:
        """
        Checks if the system is in a safe state.
        Returns a tuple: (is_safe, safe_sequence)
        """
        work = self.available[:]
        finish = [False] * self.num_processes
        safe_sequence = []
        
        while len(safe_sequence) < self.num_processes:
            allocated_in_this_pass = False
            
            for i in range(self.num_processes):
                if not finish[i]:
                    # Check if Need <= Work for all resources
                    can_allocate = True
                    for j in range(self.num_resources):
                        if self.need[i][j] > work[j]:
                            can_allocate = False
                            break
                            
                    if can_allocate:
                        # Simulate allocation and completion
                        for j in range(self.num_resources):
                            work[j] += self.allocation[i][j]
                        
                        finish[i] = True
                        safe_sequence.append(self.processes[i])
                        allocated_in_this_pass = True
            
            # If we went through all processes and couldn't satisfy any, it's unsafe
            if not allocated_in_this_pass:
                return False, []
                
        return True, safe_sequence

    def request_resources(self, process_index: int, request: List[int]) -> Tuple[bool, str]:
        """
        Simulates a process requesting resources.
        Returns (success, message)
        """
        # 1. Check if Request <= Need
        for j in range(self.num_resources):
            if request[j] > self.need[process_index][j]:
                return False, f"Error: Process has exceeded its maximum claim."
                
        # 2. Check if Request <= Available
        for j in range(self.num_resources):
            if request[j] > self.available[j]:
                return False, f"Process must wait, resources not available."
                
        # 3. Pretend to allocate
        for j in range(self.num_resources):
            self.available[j] -= request[j]
            self.allocation[process_index][j] += request[j]
            self.need[process_index][j] -= request[j]
            
        # 4. Check if the new state is safe
        is_safe, sequence = self.is_safe_state()
        
        if is_safe:
            return True, f"Request granted. System is SAFE. Safe sequence: {' -> '.join(sequence)}"
        else:
            # Rollback since it's unsafe
            for j in range(self.num_resources):
                self.available[j] += request[j]
                self.allocation[process_index][j] -= request[j]
                self.need[process_index][j] += request[j]
            return False, f"Request denied. System would enter an UNSAFE state (Deadlock possible)."

    def print_state(self):
        print("\nCurrent System Resource State")
        print("-" * 60)
        print(f"Available Resources: {self.available}")
        print(f"{'PID':<6} | {'Allocation':<15} | {'Max Claim':<15} | {'Need':<15}")
        print("-" * 60)
        for i in range(self.num_processes):
            alloc = str(self.allocation[i])
            max_c = str(self.max_claim[i])
            need_str = str(self.need[i])
            print(f"{self.processes[i]:<6} | {alloc:<15} | {max_c:<15} | {need_str:<15}")
        print("-" * 60)

def run_bankers_demo():
    print("\nBanker's Algorithm Demo (Deadlock Avoidance)")
    print("=" * 80)
    
    processes = ["P0", "P1", "P2", "P3", "P4"]
    
    # Available instances of resources A, B, C
    available = [3, 3, 2]
    
    # Maximum instances of resources that processes will request
    max_claim = [
        [7, 5, 3],
        [3, 2, 2],
        [9, 0, 2],
        [2, 2, 2],
        [4, 3, 3]
    ]
    
    # Resources currently allocated to processes
    allocation = [
        [0, 1, 0],
        [2, 0, 0],
        [3, 0, 2],
        [2, 1, 1],
        [0, 0, 2]
    ]
    
    banker = BankersAlgorithm(processes, available, max_claim, allocation)
    banker.print_state()
    
    is_safe, sequence = banker.is_safe_state()
    if is_safe:
        print(f"\nInitial State is SAFE. Safe Sequence: {' -> '.join(sequence)}")
    else:
        print("\nInitial State is UNSAFE (Deadlock possible).")
        
    # Test a safe request
    print("\n--- Testing Request: P1 requests [1, 0, 2] ---")
    success, msg = banker.request_resources(1, [1, 0, 2])
    print(msg)
    if success:
        banker.print_state()
        
    # Test an unsafe request
    print("\n--- Testing Request: P4 requests [3, 3, 0] ---")
    success, msg = banker.request_resources(4, [3, 3, 0])
    print(msg)
    print("=" * 80)
    
    return is_safe
