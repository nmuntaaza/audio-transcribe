import librosa
from . import noise_reduction as nr
from . import utils as apu
from . import audio_diarization as ad
from . import speech_to_text as stt
from flask import current_app
import os


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
        speaker_speech_1, speaker_speech_2 = ad.audio_diarization(reduced_audio, audio_samplerate, 2, False)

        # Masing-masing speech disimpan dulu pada storage untuk digunakan saat conver_to_binary
        one_temp_filename = apu.write_to_wav(speaker_speech_1, audio_samplerate)
        two_temp_filename = apu.write_to_wav(speaker_speech_2, audio_samplerate)
        print(one_temp_filename, two_temp_filename)

        path_audio_one = f"{current_app.config['TEMP_FOLDER']}{one_temp_filename}.wav"
        path_audio_two = f"{current_app.config['TEMP_FOLDER']}{two_temp_filename}.wav"
        one_blob_filename = f"tempfile/{one_temp_filename}.wav"
        two_blob_filename = f"tempfile/{two_temp_filename}.wav"

        bucket_one = stt.upload_to_bucket(one_blob_filename, path_audio_one, "kota-108")
        bucket_two = stt.upload_to_bucket(two_blob_filename, path_audio_two, "kota-108")

        apu.clear_folder(current_app.config['TEMP_FOLDER'])

        bucket_one = f"gs://kota-108/tempfile/{one_temp_filename}.wav"
        bucket_two = f"gs://kota-108/tempfile/{two_temp_filename}.wav"

        # Transkripsi Speaker 1
        response_transcribe_one = stt.transcribe_audio(bucket_one)
        response_transcribe_two = stt.transcribe_audio(bucket_two)

        transcript_one = stt.process_transcript(response_transcribe_one, 1)
        transcript_two = stt.process_transcript(response_transcribe_two, 2)

        transcript_dialog = stt.sort_transcript(transcript_one, transcript_two)
        print(f"Transcript One {transcript_one}")
        print(f"Transcript Two {transcript_two}")
        print(stt.generate_dialogue(transcript_dialog))

    except ValueError as err:
        print(err)
        return False

    return True


def reduce_noise(audio, audio_sr, noise_start_time, noise_end_time):
    audio_noise = nr.get_noise(audio, noise_start_time, noise_end_time, audio_sr)
    reduced_audio = nr.remove_noise(audio, audio_noise, verbose=True)

    return reduced_audio
