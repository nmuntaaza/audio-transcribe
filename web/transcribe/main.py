import librosa
import numpy as np
from . import noise_reduction as nr
from . import noise_generator as ng
from . import utils as apu


def main():
    y, sr = librosa.load("./resources/wav/Decoded/Sampel2a.wav", sr=44100)

    y = reduce_noise(y, sr, 2)
    y, time_trimmed = apu.trim_silence(y)
    y = librosa.util.normalize(y, norm=np.inf)
    librosa.output.write_wav("./resources/output/Sampel2_Reduce2.wav", y, sr)
    pass


def reduce_noise(y, sr, noise_len=2):
    noise_reduction = nr.NoiseReduction()
    # noise_generator = ng.NoiseGenerator()
    noise, sr = librosa.load("./resources/wav/Noise2a.wav", sr=44100)
    # Generate Noise
    # noise = noise_generator.band_limiter_noise(sr, len(y))*10 # Revision
    # noise_clip = noise[:noise_len*sr]
    # audio_clip_band_limiter = y+noise

    # noise_clip, sr2 = librosa.load("./resources/wav/Street_Noise.wav", sr=44100)
    # output = noise_reduction.remove_noise(y, noise_clip, verbose=True)
    output = noise_reduction.remove_noise(y, noise, verbose=True)
    output = noise_reduction.reduce_noise_power(output, sr)

    return output


def generate_noise(y, sr):
    noise_generator = ng.NoiseGenerator()
    samplerates = [8000, 16000, 32000, 44100]
    noise_len = 2

    for sr in samplerates:
        noise = noise_generator.band_limiter_noise(sr, len(y))*10
        noise_clip = noise[:noise_len*sr]
        try:
            librosa.output.write_wav("./resources/noise_clip_"+str(sr)+"hz.wav", noise_clip, sr)
            print("Generate Noise {} Hz Success!".format(sr))
        except:
            print("Generate Noise {} Hz Not Success!".format(sr))


if __name__ == "__main__":
    exit(main())
