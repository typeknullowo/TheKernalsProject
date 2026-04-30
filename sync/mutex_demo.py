import threading
import time


def run_sync_demo():
    print("\nSynchronization Demo: Producer-Consumer Problem")
    print("=" * 80)
    
    # --- NO LOCK SCENARIO ---
    print("\n1. NO-LOCK SCENARIO (Demonstrating Race Condition)")
    print("-" * 80)
    event_log_no_lock = []
    buffer_count = [0]  # Using list to make it mutable inside threads
    
    def producer_no_lock():
        for _ in range(3):
            event_log_no_lock.append("[Producer] State: Active | Attempting to produce")
            # Simulated race condition: read, sleep, write
            temp = buffer_count[0]
            time.sleep(0.01)  # Context switch simulation
            buffer_count[0] = temp + 1
            event_log_no_lock.append(f"[Producer] State: Active | Added item. Buffer count is now {buffer_count[0]}")
            
    def consumer_no_lock():
        for _ in range(3):
            event_log_no_lock.append("[Consumer] State: Active | Attempting to consume")
            temp = buffer_count[0]
            time.sleep(0.01)  # Context switch simulation
            buffer_count[0] = temp - 1
            event_log_no_lock.append(f"[Consumer] State: Active | Removed item. Buffer count is now {buffer_count[0]}")
            
    t1 = threading.Thread(target=producer_no_lock)
    t2 = threading.Thread(target=consumer_no_lock)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    
    for event in event_log_no_lock:
        print(event)
    print(f"--> Final buffer count (expected 0): {buffer_count[0]} (WARNING: Data inconsistency due to race condition!)\n")


    # --- MUTEX / SEMAPHORE SCENARIO ---
    print("2. MUTEX & SEMAPHORE SCENARIO (Safe Execution)")
    print("-" * 80)
    event_log_lock = []
    buffer = []
    BUFFER_SIZE = 2
    
    mutex = threading.Lock()
    empty = threading.Semaphore(BUFFER_SIZE)
    full = threading.Semaphore(0)
    
    def producer_lock():
        for i in range(3):
            event_log_lock.append("[Producer] State: Waiting | Waiting for empty slot...")
            empty.acquire()
            event_log_lock.append("[Producer] State: Waiting | Acquired empty slot. Waiting for mutex...")
            mutex.acquire()
            
            # Critical Section
            event_log_lock.append("[Producer] State: Running | Producing item.")
            buffer.append(f"item_{i}")
            event_log_lock.append(f"[Producer] State: Running | Added item. Buffer: {len(buffer)}/{BUFFER_SIZE}")
            
            mutex.release()
            full.release()
            time.sleep(0.01)
            
    def consumer_lock():
        for _ in range(3):
            event_log_lock.append("[Consumer] State: Waiting | Waiting for full slot...")
            full.acquire()
            event_log_lock.append("[Consumer] State: Waiting | Acquired full slot. Waiting for mutex...")
            mutex.acquire()
            
            # Critical Section
            event_log_lock.append("[Consumer] State: Running | Consuming item.")
            item = buffer.pop(0)
            event_log_lock.append(f"[Consumer] State: Running | Removed {item}. Buffer: {len(buffer)}/{BUFFER_SIZE}")
            
            mutex.release()
            empty.release()
            time.sleep(0.02)
            
    t3 = threading.Thread(target=producer_lock)
    t4 = threading.Thread(target=consumer_lock)
    t3.start()
    t4.start()
    t3.join()
    t4.join()
    
    for event in event_log_lock:
        print(event)
    print(f"--> Final buffer count (expected 0): {len(buffer)} (SUCCESS: Data is consistent!)")
    print("=" * 80)

