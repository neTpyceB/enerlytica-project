from collections import defaultdict
from threading import Lock


class MetricsRegistry:
    def __init__(self) -> None:
        self._lock = Lock()
        self._counters: dict[str, float] = defaultdict(float)
        self._gauges: dict[str, float] = {}

        self._counters["enerlytica_records_received_total"] = 0.0
        self._counters["enerlytica_records_accepted_total"] = 0.0
        self._counters["enerlytica_records_rejected_total"] = 0.0
        self._counters["enerlytica_duplicates_detected_total"] = 0.0
        self._counters["enerlytica_aggregation_runs_total"] = 0.0
        self._counters["enerlytica_aggregation_failures_total"] = 0.0

    def inc_counter(self, name: str, value: float = 1.0) -> None:
        with self._lock:
            self._counters[name] += value

    def set_gauge(self, name: str, value: float) -> None:
        with self._lock:
            self._gauges[name] = value

    def snapshot(self) -> tuple[dict[str, float], dict[str, float]]:
        with self._lock:
            return dict(self._counters), dict(self._gauges)


METRICS = MetricsRegistry()


def render_prometheus_text(counters: dict[str, float], gauges: dict[str, float]) -> str:
    lines: list[str] = []

    for name in sorted(counters):
        lines.append(f"# TYPE {name} counter")
        lines.append(f"{name} {counters[name]}")

    for name in sorted(gauges):
        lines.append(f"# TYPE {name} gauge")
        lines.append(f"{name} {gauges[name]}")

    return "\n".join(lines) + "\n"
