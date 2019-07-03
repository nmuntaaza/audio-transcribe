import numpy as np

    
def fftnoise(self, f):
    """Create noise with Fast Fourier Transform

    Arguments:
        f {ndarray} -- FFT Frequency

    Returns:
        ndarray -- FFT
    """

    f = np.array(f, "complex")
    Np = (len(f) - 1)
    phases = np.random.rand(Np) * 2 * np.pi
    phases = np.cos(phases) + 1j * np.sin(phases)
    f[1:Np+1] *= phases
    f[-1:-1-Np:-1] = np.conj(f[1:Np+1])

    return np.fft.ifft(f).real


def band_limiter_noise(self, samplerate, samples, min_freq=4000, max_freq=12000):
    """
    Comment
    """
    freqs = np.abs(np.fft.fftfreq(samples, 1/samplerate))
    f = np.zeros(samples)
    f[np.logical_and(freqs >= min_freq, freqs <= max_freq)] = 1

    return self.fftnoise(f)
