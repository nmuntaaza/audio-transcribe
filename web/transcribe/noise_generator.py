import numpy as np
import librosa

    
def fftnoise(f):
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


def band_limiter_noise(samplerate, samples, min_freq=4000, max_freq=12000):
    """
    Comment
    """
    freqs = np.abs(np.fft.fftfreq(samples, 1/samplerate))
    f = np.zeros(samples)
    f[np.logical_and(freqs >= min_freq, freqs <= max_freq)] = 1

    return self.fftnoise(f)


def generate_noise(y, sr):
    noise_len = 2

    noise = band_limiter_noise(sr, len(y)) * 10
    noise_clip = noise[:noise_len*sr]
    try:
        librosa.output.write_wav("./resources/noise_clip_"+str(sr)+"hz.wav", noise_clip, sr)
        print("Generate Noise {} Hz Success!".format(sr))
    except:
        print("Generate Noise {} Hz Not Success!".format(sr))
