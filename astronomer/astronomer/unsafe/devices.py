from contextlib import contextmanager
import math
import random
from subprocess import run, CalledProcessError
import time

import numpy as np

from .. import settings


class TestSDR:

    sample_rate = 1e6
    center_freq = 1e6
    bandwidth = 1e6
    gain = 10

    def set_bias_tee(self, value, device_index=0):
        pass

    def test_device(self, n, delay=2):
        time.sleep(delay)
        return True

    def read_samples(self, destination_path, n):
        time.sleep(n // self.sample_rate // 2)  # The test device is faster than normal.

        t = random.random()
        Ax, Ay  = random.random(), random.random()
        data = np.array([
            complex(
                Ax * math.sin(x*self.center_freq + t)
                + Ay * math.cos(x*self.center_freq + t))
            for x in range(n)
        ]) + np.random.normal(0, 1, n)

        with open(destination_path, 'wb') as f:
            f.write(data.tobytes())


class RTLSDR:

    sample_rate = 1e6
    center_freq = 1e6
    bandwidth = 1e6
    gain = 10
    ppm = 0

    def test_device(self, n=10, device_index=0):
        try:
            self.read_samples('/dev/null', n, device_index=device_index)
        except CalledProcessError as e:
            return False
        else:
            return True

    def set_bias_tee(self, value, device_index=0):
        value = 1 if value else 0
        command = f'rtl_biast -d {device_index} -b {value}'

        try:
            run(
                command,
                shell=True,
                check=True,
                cwd=settings.CAPTURE_DATA_PATH,
                capture_output=True,
            )
        except CalledProcessError as e:
            return False
        else:
            return True

    def read_samples(self, destination_path, n, device_index=0):
        """ Take a reading from the device given the settings provided
        and save those to the a file as a compressed archive.
        """
        command = f"""
            rtl_sdr \
                -f {self.center_freq} \
                -s {self.sample_rate} \
                -d {device_index} \
                -g {self.gain} \
                -p {self.ppm} \
                -S \
                -n {n} \
                {destination_path}
        """
        return run(
            command,
            shell=True,
            capture_output=True,
            cwd=settings.CAPTURE_DATA_PATH,
        )


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
            self.bias_tee = bias_tee
        else:
            self.sdr = RTLSDR()
            self.bias_tee = bias_tee

    def set_settings(
        self,
        sample_rate=None,
        frequency=None,
        bandwidth=None,
        gain=None,
    ):
        self.sdr.set_bias_tee(self.bias_tee)
        if sample_rate:
            self.sdr.sample_rate = sample_rate
        if frequency:
            self.sdr.center_freq = frequency
        if bandwidth:
            self.sdr.bandwidth = bandwidth
        if gain:
            self.sdr.gain = gain

    def test(self, n=1, **kwargs):
        try:
            self.set_settings(**kwargs)
            self.sdr.test_device(n)
        except Exception:
            return False
        else:
            return True

    def read(self, destination_path, n, **kwargs):
        self.set_settings(**kwargs)
        return self.sdr.read_samples(destination_path, n)
