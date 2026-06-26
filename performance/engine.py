import time
import psutil
import os
import json
from datetime import datetime

class PerformanceTracker:
    def __init__(self, label: str = "unnamed"):
        self.label = label
        self.process = psutil.Process(os.getpid())
        self._start_time = None
        self._start_cpu = None
        self._start_mem = None
        self.results = {}

    def start(self):
        self._start_time = time.time()
        self._start_cpu = self.process.cpu_percent(interval=None)
        self._start_mem = self.process.memory_info().rss / (1024 * 1024)  # MB
        print(f"[Perf] Starting: {self.label}")

    def stop(self, agents_completed: int = 1):
        end_time = time.time()
        end_mem = self.process.memory_info().rss / (1024 * 1024)
        cpu_now = self.process.cpu_percent(interval=0.1)

        duration = end_time - self._start_time

        self.results = {
            "label": self.label,
            "timestamp": datetime.now().isoformat(),
            "duration_seconds": round(duration, 3),
            "cpu_percent": round(cpu_now, 2),
            "memory_start_mb": round(self._start_mem, 2),
            "memory_end_mb": round(end_mem, 2),
            "memory_delta_mb": round(end_mem - self._start_mem, 2),
            "agents_completed": agents_completed,
            "throughput_agents_per_sec": round(agents_completed / duration, 3) if duration > 0 else 0
        }
        return self.results

    def save(self, path: str = "reports/perf_baseline.json"):
        os.makedirs("reports", exist_ok=True)
        
        # Load existing or start new list
        existing = []
        if os.path.exists(path):
            with open(path, "r") as f:
                existing = json.load(f)
        
        existing.append(self.results)
        with open(path, "w") as f:
            json.dump(existing, f, indent=2)
        print(f"[Perf] Saved to {path}")

    def report(self) -> dict:
        return self.results