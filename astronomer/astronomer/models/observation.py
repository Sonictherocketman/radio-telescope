from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Observation:
    identifier: str
    frequency: int
    sample_rate: int
    gain: int
    bandwidth: int
    signal: [complex]
    timestamp = None
    calibration: Observation = None


