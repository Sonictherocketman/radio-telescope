from dataclasses import dataclass, field


@dataclass
class FixedBuffer:
    length: int
    _data: [[float]] = field(default_factory=list)

    def add(self, samples: [float]):
        self._data.insert(0, samples)
        self._data = self._data[:self.length]

    def get_data(self) -> [[float]]:
        return self._data

    @property
    def percent_full(self):
        return len(self._data) / self.length

