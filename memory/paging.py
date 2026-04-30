from typing import List


def run_fifo(reference_string: List[int], num_frames: int) -> dict:
    frames = []
    faults = 0
    hits = 0
    history = []
    
    for page in reference_string:
        if page in frames:
            hits += 1
            history.append((page, "Hit", list(frames)))
        else:
            faults += 1
            if len(frames) < num_frames:
                frames.append(page)
            else:
                frames.pop(0)
                frames.append(page)
            history.append((page, "Fault", list(frames)))
            
    return {"algorithm": "FIFO", "hits": hits, "faults": faults, "history": history}


def run_lru(reference_string: List[int], num_frames: int) -> dict:
    frames = []
    faults = 0
    hits = 0
    history = []
    
    for page in reference_string:
        if page in frames:
            hits += 1
            frames.remove(page)
            frames.append(page)
            history.append((page, "Hit", list(frames)))
        else:
            faults += 1
            if len(frames) < num_frames:
                frames.append(page)
            else:
                frames.pop(0)
                frames.append(page)
            history.append((page, "Fault", list(frames)))
            
    return {"algorithm": "LRU", "hits": hits, "faults": faults, "history": history}


def run_optimal(reference_string: List[int], num_frames: int) -> dict:
    frames = []
    faults = 0
    hits = 0
    history = []
    
    for i, page in enumerate(reference_string):
        if page in frames:
            hits += 1
            history.append((page, "Hit", list(frames)))
        else:
            faults += 1
            if len(frames) < num_frames:
                frames.append(page)
            else:
                farthest = -1
                replace_idx = -1
                for j, frame_page in enumerate(frames):
                    try:
                        next_use = reference_string[i+1:].index(frame_page)
                    except ValueError:
                        replace_idx = j
                        break
                    
                    if next_use > farthest:
                        farthest = next_use
                        replace_idx = j
                        
                frames[replace_idx] = page
            history.append((page, "Fault", list(frames)))
            
    return {"algorithm": "Optimal", "hits": hits, "faults": faults, "history": history}


def print_paging_result(result: dict):
    print(f"\n--- {result['algorithm']} Page Replacement ---")
    print(f"{'Page':<6} | {'Action':<6} | {'Frames'}")
    print("-" * 35)
    for page, action, frames in result["history"]:
        print(f"{page:<6} | {action:<6} | {frames}")
    print("-" * 35)
    print(f"Total Hits:   {result['hits']}")
    print(f"Total Faults: {result['faults']}")
    
    fault_rate = (result['faults'] / len(result['history'])) * 100 if result['history'] else 0
    print(f"Fault Rate:   {fault_rate:.2f}%")


def run_paging_demo():
    print("\nVirtual Memory Demo (Page Replacement Algorithms)")
    print("=" * 80)
    
    reference_string = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2]
    num_frames = 3
    
    print(f"Reference String: {reference_string}")
    print(f"Number of Frames: {num_frames}")
    
    fifo_result = run_fifo(reference_string, num_frames)
    print_paging_result(fifo_result)
    
    lru_result = run_lru(reference_string, num_frames)
    print_paging_result(lru_result)
    
    opt_result = run_optimal(reference_string, num_frames)
    print_paging_result(opt_result)
    print("=" * 80)
    
    return [fifo_result, lru_result, opt_result]
