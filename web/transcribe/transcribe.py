import librosa
from . import noise_reduction as nr
from . import utils as apu
from . import audio_diarization as ad
from . import speech_to_text as stt
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

        # Diarization
        speaker_speech = ad.audio_diarization(reduced_audio, audio_samplerate, 2, True)

        # Masing masing speech disimpan dulu pada storage untuk digunakan saat conver_to_binary
        temp_one = apu.write_to_wav(speaker_speech[0], audio_samplerate)
        temp_two = apu.write_to_wav(speaker_speech[1], audio_samplerate)

        path_one = "../wavtemp/{}.wav".format(temp_one)
        path_two = "../wavtemp/{}.wav".format(temp_two)
        blob_one = "tempfile/{}.wav".format(temp_one)
        blob_two = "tempfile/{}.wav".format(temp_two)

        bucket_one = stt.upload_to_bucket(blob_one, path_one, "kota-108")
        bucket_two = stt.upload_to_bucket(blob_two, path_two, "kota-108")

        apu.remove_file(path_one)
        apu.remove_file(path_two)

    except ValueError as err:
        print(err)
        return False

    return True


def reduce_noise(audio, audio_sr, noise_start_time, noise_end_time):
    audio_noise = nr.get_noise(audio, noise_start_time, noise_end_time, audio_sr)
    reduced_audio = nr.remove_noise(audio, audio_noise, verbose=True)

    return reduced_audio
