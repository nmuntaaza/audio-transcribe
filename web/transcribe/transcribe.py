import librosa
import numpy as np
from . import noise_reduction as nr
from . import noise_generator as ng
from . import utils as apu
from . import audio_diarization
from flask import current_app


def transcribe(audio_file_name, noise_start_time=1, noise_end_time=3, verbose=False):
    # Cek Apabila nama terdapat ekstensinya (Not done)
    audio_path = current_app.config['UPLOAD_FOLDER'] + audio_file_name
    # Convert file audio dari raw ke wav pcm linear
    apu.convert_audio(audio_path, audio_path)

    audio, audio_samplerate = librosa.load(audio_path, sr=None)

    try:
        # Filtering
        filtered_audio = nr.butter_bandpass_filter(audio, 85, 255, audio_samplerate)
        if verbose:
            audio_output_path = current_app.config['UPLOAD_FOLDER'] + "filtered_" + audio_file_name
            librosa.output.write_wav(audio_output_path, filtered_audio, audio_samplerate, norm=False)

        # Reduction
        reduced_audio = reduce_noise(filtered_audio, audio_samplerate, noise_start_time, noise_end_time)
        if verbose:
            audio_output_path = current_app.config['UPLOAD_FOLDER'] + "reduced_" + audio_file_name
            librosa.output.write_wav(audio_output_path, reduced_audio, audio_samplerate, norm=False)
        
        # #audio, time_trimmed = apu.trim_silence(audio)
    except ValueError as err:
        return False

    return True


def reduce_noise(audio, audio_sr, noise_start_time, noise_end_time):
    audio_noise = nr.get_noise(audio, noise_start_time, noise_end_time, audio_sr)
    print("get_noise")
    reduced_audio = nr.remove_noise(audio, audio_noise, verbose=True)
    print("remove_noise")

    return reduced_audio


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
