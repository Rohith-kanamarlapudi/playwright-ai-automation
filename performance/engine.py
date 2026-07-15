import json
import os
import time
from datetime import datetime
from pathlib import Path

import psutil


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
        self._start_mem = (
            self.process.memory_info().rss / (1024 * 1024)
        )

        print(f"[Perf] Starting: {self.label}")

    def stop(self, agents_completed: int = 1):

        end_time = time.time()

        end_mem = (
            self.process.memory_info().rss / (1024 * 1024)
        )

        cpu_now = self.process.cpu_percent(interval=0.1)

        duration = end_time - self._start_time

        self.results = {
            "label": self.label,
            "timestamp": datetime.now().isoformat(),
            "duration_seconds": round(duration, 3),
            "cpu_percent": round(cpu_now, 2),
            "memory_start_mb": round(self._start_mem, 2),
            "memory_end_mb": round(end_mem, 2),
            "memory_delta_mb": round(
                end_mem - self._start_mem,
                2,
            ),
            "agents_completed": agents_completed,
            "throughput_agents_per_sec": (
                round(
                    agents_completed / duration,
                    3,
                )
                if duration > 0
                else 0
            ),
        }

        return self.results

    def save(
        self,
        path: str = "reports/perf_baseline.json",
    ):
        """
        Save performance results.

        Handles:
        - missing file
        - empty file
        - corrupted JSON
        - single-object JSON
        """

        repo_root = Path(__file__).resolve().parent.parent

        resolved = repo_root / path

        resolved.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        existing = []

        if resolved.exists():

            try:

                with open(
                    resolved,
                    "r",
                    encoding="utf-8",
                ) as f:

                    content = f.read().strip()

                    if content:

                        existing = json.loads(content)

                        # Older versions may contain
                        # a single JSON object instead
                        # of a list.
                        if isinstance(existing, dict):
                            existing = [existing]

                    else:
                        existing = []

            except json.JSONDecodeError as e:

                print(
                    "[Perf] Warning: Corrupted performance "
                    "JSON detected."
                )

                print(
                    f"[Perf] JSON error: {e}"
                )

                backup = resolved.with_suffix(".corrupted.json")

                try:
                    resolved.rename(backup)

                    print(
                        f"[Perf] Corrupted file renamed to:\n"
                        f"       {backup}"
                    )

                except Exception:
                    pass

                existing = []

            except Exception as e:

                print(
                    f"[Perf] Failed to read existing "
                    f"performance log: {e}"
                )

                existing = []

        existing.append(self.results)

        with open(
            resolved,
            "w",
            encoding="utf-8",
        ) as f:

            json.dump(
                existing,
                f,
                indent=2,
            )

        print(f"[Perf] Saved to {resolved}")

    def report(self) -> dict:
        return self.results