from pylab import *
from rtlsdr import *

sdr = RtlSdr()

# configure device
sdr.sample_rate = 3.2e6
sdr.center_freq = 1.4204e9
sdr.gain = 49.6

# samples_test = sdr.read_samples(1024*1024)
samples_calibrate = sdr.read_samples(65536*1024)

samples_observe = sdr.read_samples(65536*1024)
sdr.close()

psd_values_observe, freq = psd(
    samples_observe,
    NFFT=1024,
    Fs=sdr.sample_rate/1e6,
    Fc=sdr.center_freq/1e6
)

psd_values_calibrate, freq = psd(
    samples_calibrate,
    NFFT=1024,
    Fs=sdr.sample_rate/1e6,
    Fc=sdr.center_freq/1e6
)

plot(freqs, psd_values_observe - psd_values_calibrate)
xlabel('Frequency (MHz)')
ylabel('Relative power (dB)')
show()
