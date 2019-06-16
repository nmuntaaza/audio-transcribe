import librosa
import subprocess


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
    except subprocess.CalledProcessError:
        return False
    
    return True
