from typing import List
from models.memory_block import MemoryBlock

def first_fit(blocks: List[MemoryBlock], process_id: str, request_size: int) -> bool:
    """
    First Fit Memory Allocation
    Allocates the first available block that is large enough.
    """
    for block in blocks:
        if block.is_free and block.size >= request_size:
            block.allocated_to = process_id
            block.allocated_size = request_size
            return True
    return False

def best_fit(blocks: List[MemoryBlock], process_id: str, request_size: int) -> bool:
    """
    Best Fit Memory Allocation
    Allocates the smallest available block that is large enough.
    """
    best_idx = -1
    min_diff = float('inf')
    
    for i, block in enumerate(blocks):
        if block.is_free and block.size >= request_size:
            diff = block.size - request_size
            if diff < min_diff:
                min_diff = diff
                best_idx = i
                
    if best_idx != -1:
        blocks[best_idx].allocated_to = process_id
        blocks[best_idx].allocated_size = request_size
        return True
    return False

def print_memory_state(title: str, blocks: List[MemoryBlock]):
    print(f"\n{title}")
    print("-" * 75)
    print(f"{'Block ID':<10} | {'Total Size':<12} | {'Status':<20} | {'Fragmentation':<15}")
    print("-" * 75)
    
    total_free = 0
    total_frag = 0
    
    for block in blocks:
        if block.is_free:
            status = "Free"
            total_free += block.size
            frag_str = "-"
        else:
            status = f"Allocated ({block.allocated_to})"
            total_frag += block.fragmentation
            frag_str = str(block.fragmentation)
            
        print(f"{block.id:<10} | {block.size:<12} | {status:<20} | {frag_str:<15}")
        
    print("-" * 75)
    print(f"Total Free Memory: {total_free}")
    print(f"Total Internal Fragmentation: {total_frag}")
    print("=" * 75)

def run_memory_demo():
    print("\nMain Memory Management Demo (First Fit vs Best Fit)")
    print("=" * 80)
    
    # Base configuration for both tests
    def get_fresh_blocks():
        return [
            MemoryBlock(1, 100),
            MemoryBlock(2, 500),
            MemoryBlock(3, 200),
            MemoryBlock(4, 300),
            MemoryBlock(5, 600)
        ]
    
    requests = [
        ("P1", 212),
        ("P2", 417),
        ("P3", 112),
        ("P4", 426)
    ]
    
    # 1. First Fit Test
    blocks_ff = get_fresh_blocks()
    print("\n--- FIRST FIT ALLOCATION ---")
    for pid, size in requests:
        success = first_fit(blocks_ff, pid, size)
        if success:
            print(f"[+] Allocated {pid} ({size} units)")
        else:
            print(f"[-] Failed to allocate {pid} ({size} units) - No suitable block found.")
            
    print_memory_state("Memory State after First Fit", blocks_ff)
    
    # 2. Best Fit Test
    blocks_bf = get_fresh_blocks()
    print("\n--- BEST FIT ALLOCATION ---")
    for pid, size in requests:
        success = best_fit(blocks_bf, pid, size)
        if success:
            print(f"[+] Allocated {pid} ({size} units)")
        else:
            print(f"[-] Failed to allocate {pid} ({size} units) - No suitable block found.")
            
    print_memory_state("Memory State after Best Fit", blocks_bf)
