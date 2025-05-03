from __future__ import annotations

from datetime import datetime
from dataclasses import dataclass


@dataclass
class AbstractObservation:
    identifier: str
    frequency: int
    sample_rate: int
    gain: int
    bandwidth: int
    timestamp: str = None

    @property
    def meta(self) -> dict:
        return dict(
            identifier=self.identifier,
            frequency=self.frequency,
            sample_rate=self.sample_rate,
            gain=self.gain,
            bandwidth=self.bandwidth,
            timestamp=self.timestamp,
        )


@dataclass
class Calibration(AbstractObservation):
    pass


@dataclass
class Observation(AbstractObservation):
    calibration: Observation = None

    @property
    def summary(self) -> str:
        return (
            f'{self.identifier} (gain={self.gain}, freq={self.frequency}) '
            f'sr={self.sample_rate}, bw={self.bandwidth}, '
            f'c={bool(self.calibration)})'
        )

    @property
    def meta(self) -> dict:
        if self.calibration:
            return dict(**super().meta, calibration=self.calibration.meta)
        else:
            return super().meta
