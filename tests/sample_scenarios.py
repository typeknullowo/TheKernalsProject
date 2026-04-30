from models.process import Process

def get_sample_processes():
    return [
        Process("P1", arrival_time=0, burst_time=5, priority=3),
        Process("P2", arrival_time=1, burst_time=3, priority=1),
        Process("P3", arrival_time=2, burst_time=2, priority=4),
        Process("P4", arrival_time=4, burst_time=1, priority=2),
    ]

# Keep sample_processes for backwards compatibility
sample_processes = get_sample_processes()