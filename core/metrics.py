# core/metrics.py

import time

def measure_latency(start_time):
    return (time.perf_counter() - start_time) * 1000
