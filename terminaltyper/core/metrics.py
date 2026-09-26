"""
Combat telemetry and typing calculation engine.
Implements the exact formulas defined in Section 5 of the Game Design Document.
"""

from dataclasses import dataclass
import time


@dataclass
class TypingMetrics:
    target: str
    typed: str
    elapsed_seconds: float
    elapsed_minutes: float
    gross_wpm: float
    matching_chars: int
    accuracy: float
    net_wpm: float
    is_crit: bool
    crit_multiplier: float


def calculate_metrics(
    target: str,
    typed: str,
    elapsed_seconds: float,
    crit_threshold: float = 70.0
) -> TypingMetrics:
    """
    Calculates Gross WPM, Accuracy, Net WPM, and Critical Strike multiplier
    using high-resolution monotonic telemetry according to Section 5.1 & 5.2.
    """
    # Guard against negative or zero elapsed time
    safe_seconds = max(0.001, elapsed_seconds)
    elapsed_minutes = safe_seconds / 60.0

    # Gross WPM = (Length of Typed Input / 5.0) / Elapsed Minutes
    typed_len = len(typed)
    target_len = len(target)
    gross_wpm = (typed_len / 5.0) / elapsed_minutes

    # Matching Characters = sum([T[i] == U[i]]) for i in 0 .. min(len(T), len(U)) - 1
    min_len = min(target_len, typed_len)
    matching_chars = sum(1 for i in range(min_len) if target[i] == typed[i])

    # Accuracy = Matching Characters / max(len(Target T), len(Typed U))
    max_len = max(target_len, typed_len)
    accuracy = (matching_chars / max_len) if max_len > 0 else 0.0

    # Net WPM = Gross WPM * Accuracy
    net_wpm = gross_wpm * accuracy

    # Critical Strike Multiplier:
    # If Accuracy == 100% AND Net WPM >= crit_threshold, Crit = 1.5. Otherwise Crit = 1.0.
    is_crit = (accuracy >= 1.0) and (net_wpm >= crit_threshold)
    crit_multiplier = 1.5 if is_crit else 1.0

    return TypingMetrics(
        target=target,
        typed=typed,
        elapsed_seconds=safe_seconds,
        elapsed_minutes=elapsed_minutes,
        gross_wpm=gross_wpm,
        matching_chars=matching_chars,
        accuracy=accuracy,
        net_wpm=net_wpm,
        is_crit=is_crit,
        crit_multiplier=crit_multiplier,
    )


class MonotonicTimer:
    """High-resolution monotonic timer using time.perf_counter()."""

    def __init__(self):
        self._start_time: float | None = None
        self._end_time: float | None = None

    def start(self) -> None:
        self._start_time = time.perf_counter()
        self._end_time = None

    def stop(self) -> float:
        if self._start_time is None:
            return 0.0
        self._end_time = time.perf_counter()
        return self.elapsed()

    def elapsed(self) -> float:
        if self._start_time is None:
            return 0.0
        if self._end_time is not None:
            return self._end_time - self._start_time
        return time.perf_counter() - self._start_time
