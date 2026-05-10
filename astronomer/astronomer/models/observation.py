from __future__ import annotations

from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class AbstractObservation:
    identifier: str
    frequency: int
    offset: int
    sample_rate: int
    gain: int
    bandwidth: int
    timestamp: str = None
    n: int = None

    @property
    def meta(self) -> dict:
        return asdict(self)

    @property
    def effective_frequency(self) -> int:
        return self.frequency + self.offset


@dataclass
class Calibration(AbstractObservation):
    pass


@dataclass
class Observation(AbstractObservation):
    calibration: Calibration = None
    attributes: object = None

    @property
    def summary(self) -> str:
        return (
            f'{self.identifier} (gain={self.gain}, freq={self.frequency}) '
            f'sr={self.sample_rate}, bw={self.bandwidth}, n={self.n}, '
            f'c={bool(self.calibration)})'
        )

    @property
    def meta(self) -> dict:
        meta = super().meta
        if self.calibration is None:
            del meta['calibration']
        return meta

@dataclass
class BufferStatus:
    percent_full: float


@dataclass
class SpectrumObservation(Observation):
    buffer_status: BufferStatus = None
