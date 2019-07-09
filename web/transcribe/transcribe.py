import librosa
import time
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
        speaker_speech_1, speaker_speech_2 = ad.audio_diarization(reduced_audio, audio_samplerate, 2, False)

        # Masing-masing speech disimpan dulu pada storage untuk digunakan saat conver_to_binary
        one_temp_filename = apu.write_to_wav(speaker_speech_1, audio_samplerate)
        two_temp_filename = apu.write_to_wav(speaker_speech_2, audio_samplerate)

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
        generated_dialogue = stt.generate_dialogue(transcript_dialog)

        # T1
        if verbose:
            print("Structure: ")
            print(transcript_one[0], "Len: {}".format(len(transcript_one)), end="\n\n")
            print("Pembicara 1:", end=" ")
            for word in transcript_one:
                print(word['word'], end=" ")

            print("Structure: ")
            print(transcript_two[0], "Len: {}".format(len(transcript_two)), end="\n\n")
            print("Pembicara 2:", end=" ")
            for word in transcript_two:
                print(word['word'], end=" ")

            # Print dict structure
            print(generated_dialogue[0], end="\n\n")

            print("Dialogue: ")
            for sentence in generated_dialogue:
                timestamp = float(sentence['timestamp'])
                miliseconds = f"{timestamp % 1:.2f}".split(".")[1]
                print(time.strftime('%H:%M:%S.', time.gmtime(timestamp)) + miliseconds, end=" ")
                print("Pembicara 1:" if sentence['label'] == 1 else "Pembicara 2:", sentence['sentence'])

        final_dialogue = []
        for sentence in generated_dialogue:
            ts = float(sentence['timestamp'])
            miliseconds = f"{ts % 1:.2f}".split(".")[1]
            timestamp = time.strftime('%M:%S.', time.gmtime(ts)) + miliseconds
            dic = {
                "timestamp": timestamp,
                "pembicara": sentence['label'],
                "sentence": sentence['sentence']
            }
            final_dialogue.append(dic)

        return final_dialogue
    except ValueError as err:
        print(err)
        return False


def reduce_noise(audio, audio_sr, noise_start_time, noise_end_time):
    audio_noise = nr.get_noise(audio, noise_start_time, noise_end_time, audio_sr)
    reduced_audio = nr.remove_noise(audio, audio_noise, verbose=True)

    return reduced_audio
