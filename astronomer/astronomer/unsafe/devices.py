from contextlib import contextmanager
import math
import random
import time

import numpy as np
from rtlsdr import RtlSdr


class TestSDR:

    sample_rate = 1e6
    frequency = 1e6
    bandwidth = 1e6
    gain = 10

    def open(self):
        pass

    def close(self):
        pass

    def read_samples(self, n):
        time.sleep(3)
        t = random.random()
        Ax, Ay  = random.random(), random.random()
        return np.array([
            complex(
                Ax * math.sin(x*self.frequency + t)
                + Ay * math.cos(x*self.frequency + t))
            for x in range(n)
        ]) + np.random.normal(0, 1, n)



class DefaultDevice:

    def __init__(
        self,
        *args,
        test_mode=False,
        bias_tee=False,
        **kwargs,
    ):
        if test_mode:
            self.sdr = TestSDR()
        else:
            self.sdr = RtlSdr()
            self.sdr.set_bias_tee(bias_tee)

    def set_settings(
        self,
        sample_rate=None,
        frequency=None,
        bandwidth=None,
        gain=None,
    ):
        if sample_rate:
            self.sdr.sample_rate = sample_rate
        if frequency:
            self.sdr.center_freq = frequency
        if bandwidth:
            self.sdr.bandwidth = bandwidth
        if gain:
            self.sdr.gain = gain

    def test(self, n=1024, **kwargs):
        try:
            self.read(n, **kwargs)
        except Exception:
            return False
        else:
            return True

    def read(self, n, **kwargs):
        self.sdr.open()
        self.set_settings(**kwargs)
        signal = self.sdr.read_samples(n)
        self.sdr.close()
        return signal
