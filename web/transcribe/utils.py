import librosa
import subprocess
import numpy as np
import uuid
import scipy.io.wavfile as scipywav
import io
import os
from web.utils import create_folder_if_not_exist
from flask import current_app
from web import web


def clear_folder(folder_name):
    """
    menghapus seluruh file yang terdapat dalam folder
    :param folder_name: string, path dari folder yang akan di bersihkan
    :return: boolean
    """
    for file in os.listdir(folder_name):
        file_path = os.path.join(folder_name, file)
        print(file_path)
        try:
            remove_file(file_path)
        except OSError as e:
            print(f"Error: {e.filename} - {e.strerror}")


def remove_file(path):
    """
    Menghapus file
    :param path: string, path dari file yang akan dihapus
    :return: boolean
    """
    """
        Deskripsi: Function untuk menghapus file

        Parameter:
            path: String

        Output:

    """
    try:
        os.unlink(path)
    except OSError as e:
        print(f"Error: {e.filename} - {e.strerror}")


def read_audio_binary(path):
    """
        Deskripsi: Function untuk membaca file .wav dalam bentuk binary

        Parameter:
            path: String

        Output:
            content: String
    """
    with io.open(path, 'rb') as audio_file:
        content = audio_file.read()
    return content


def write_to_wav(audio, sr):
    """
        Deskripsi: Function untuk menyimpan data array audio kedalam file wav

        Parameter:
            audio: Numpy array
            sr: integer

        Output:
            tempid: String
    """
    temp_id = uuid.uuid4().hex[:10].upper()
    np_audio = np.array(audio)
    audio_pcm = float_to_pcm(np_audio)
    print(os.path.join(web.config['TEMP_FOLDER']))
    create_folder_if_not_exist(os.path.join(web.config['TEMP_FOLDER']))
    file_name = f"{current_app.config['TEMP_FOLDER']}{temp_id}.wav"
    scipywav.write(file_name, sr, audio_pcm)

    return temp_id


def float_to_pcm(audio):
    """
        Deskripsi: Function untuk merubah isi data array audio dari bentuk float kedalam bentuk int16

        Parameter:
            audio: Numpy array

        Output:
            audio: Numpy array
    """
    float_limit = 1.414
    int_limit = 32767

    with np.nditer(audio, op_flags=['readwrite']) as x:
        for i in x:
            i /= float_limit
            i *= int_limit

    audio_pcm = audio.astype(np.int16)

    return audio_pcm


def trim_silence(audio):
    """
    Menghilangkan silence noise dari audio
    
    Parameter
    ----------
    audio : numpy array
        array sinyal audio
    """
    audio_trimmed, trimmed_length = librosa.effects.trim(audio, top_db=20, frame_length=2, hop_length=500)
    trimmed_length = librosa.get_duration(audio) - librosa.get_duration(audio_trimmed)

    return audio_trimmed, trimmed_length


def convert_audio(in_file, out_file):
    """
    Mengubah file wav yang diinputkkan menggunakan encoding Linear PCM
    Output yang di keluarkan akan replace file lama
    
    Parameter
    ----------
    in_file : str
        path relative file audio yang akan di ubah
    out_file : str
        path relative letak output audio akan di simpan
    """
    commands = ['ffmpeg', '-hide_banner', '-loglevel', 'panic', '-y', '-i', in_file, out_file]
    # -hide_banner, -loglevel panic digunakan untuk menghilangkan keluaran ketika process convert
    # -y digunakan untuk auto replace audio ketika convert dengan nama yang sama
    try:
        subprocess.check_call(commands)
    except subprocess.CalledProcessError as error:
        return False
    
    return True
