import numpy as np
import librosa
import time
import scipy.signal
from datetime import timedelta as td
from scipy.signal import butter, lfilter
import matplotlib.pyplot as plt


def _stft(y, n_fft, hop_length, win_length):
    return librosa.stft(y=y, n_fft=n_fft, hop_length=hop_length, win_length=win_length)


def _istft(y, hop_length, win_length):
    return librosa.istft(y, hop_length, win_length)


def _amp_to_db(x):
    return librosa.core.amplitude_to_db(x, ref=1.0, amin=1e-20, top_db=80.0)


def _db_to_amp(x,):
    return librosa.core.db_to_amplitude(x,ref=1.0)


def plot_spectrogram(signal, title):
    fig, ax = plt.subplots(figsize=(20,4))
    cax = ax.matshow(signal, origin = 'lower', aspect='auto', cmap=plt.cm.seismic, vmin=-1*np.max(np.abs(signal)), vmax=np.max(np.abs(signal)))
    fig.colorbar(cax)
    ax.set_title(title)
    plt.tight_layout()
    plt.show()


def plot_statistics_and_filter(mean_freq_noise, std_freq_noise, noise_thresh, smoothing_filter):
    fig, ax = plt.subplots(ncols=2, figsize=(20,4))
    plt_mean, = ax[0].plot(mean_freq_noise, label='Mean power of noise')
    plt_std, = ax[0].plot(std_freq_noise, label='Std. power of noise')
    plt_std, = ax[0].plot(noise_thresh, label='Noise threshold (by frequency)')
    ax[0].set_title('Threshold for mask')
    ax[0].legend()
    cax = ax[1].matshow(smoothing_filter, origin = 'lower')
    fig.colorbar(cax)
    ax[1].set_title('Filter for smoothing Mask')
    plt.show()


def remove_noise(audio_clip, noise_clip, n_grad_freq=2, n_grad_time=4, n_fft=4096, win_length=2048, hop_length=512, n_std_thresh=1.5, prop_decrease=1.0, verbose=False, visual=False):
    """
    Menghilangkan noise dari audio berdasarkan clip audio yang memiliki noisi

    Parameter
    ----------
    n_grad_freq : int
        banyaknya channel frekuensi yang akan di lakukan smoothing dengan mask
    n_grad_time :
        banyaknya channel time yang akan dilakukan smoothing dengan mask
    n_fft : int
        nilai frame audio pada kolom STFT
    win_length : int
        masing-masing frame audio windowed dengan 'window()'. Window akan menjadi panjang 'win_length' dan ditambahkan dengan nilai 0 untuk menyamai 'n_fft'
    hop_length : int
        Jumlah frame audio diantara kolom STFT
    n_std_thresh : float
        berapa banyak standar deviasi lebih keras dari nilai rata-rate desibel dari noise (pada setiap level frekuensi) yang dianggap sebagai sinyal
    prop_decrease : float
        sejauh mana noise dikurangi (1 = all. 0 = none)
    visual : bool
        menampilkan plot dari algoritma
    """
    
    if verbose: start = time.time()
        
    # STFT pada noise
    noise_stft = _stft(noise_clip, n_fft, hop_length, win_length) 
    noise_stft_db = _amp_to_db(np.abs(noise_stft))# convert ke dB
    
    # Menghitung statistik pada noise
    mean_freq_noise = np.mean(noise_stft_db, axis =1)
    std_freq_noise = np.std(noise_stft_db, axis =1)
    noise_thresh = mean_freq_noise+std_freq_noise*n_std_thresh
    
    if verbose: print('STFT on noise:', td(seconds=time.time()-start)); start = time.time()
        
    # STFT pada sinyal audio
    if verbose: start = time.time()
    sig_stft = _stft(audio_clip, n_fft, hop_length, win_length)
    sig_stft_db = _amp_to_db(np.abs(sig_stft))
    
    if verbose: print('STFT on signal:',td(seconds=time.time()-start)); start = time.time()
        
    # Menghitung nilai masing pada desibel
    mask_gain_dB = np.min(_amp_to_db(np.abs(sig_stft)))
    print(noise_thresh, mask_gain_dB)
    
    # Membuat filter smoothing untuk masking pada waktu dan frekuensi
    smoothing_filter = np.outer(np.concatenate([np.linspace(0,1,n_grad_freq+1,endpoint=False),np.linspace(1,0,n_grad_freq+2)])[1:-1], 
                       np.concatenate([np.linspace(0,1,n_grad_time+1,endpoint=False),np.linspace(1,0,n_grad_time+2)])[1:-1])
    smoothing_filter = smoothing_filter/np.sum(smoothing_filter)
    
    # Menghitung threshold pada setiap frekuensi/time bin
    db_thresh = np.repeat(np.reshape(noise_thresh, [1,len(mean_freq_noise)]), np.shape(sig_stft_db)[1], axis = 0).T
    
    # Mask apabila sinyal diatas nilai threshold
    sig_mask = sig_stft_db<db_thresh
    
    if verbose: print('Masking:', td(seconds=time.time()-start)); start = time.time()
        
    # Convolce mask dengan smoothing filter
    sig_mask = scipy.signal.fftconvolve(sig_mask, smoothing_filter,  mode='same')
    sig_mask = sig_mask*prop_decrease
    
    if verbose: print('Mask convolution:', td(seconds=time.time()-start)); start = time.time()
        
    # Mask sinyal audio
    sig_stft_db_masked = sig_stft_db *(1-sig_mask) + np.ones(np.shape(mask_gain_dB))*mask_gain_dB*sig_mask # mask real
    sig_imag_masked = np.imag(sig_stft)*(1-sig_mask)
    sig_stft_amp = ((_db_to_amp(sig_stft_db_masked)*np.sign(sig_stft))+(1j * sig_imag_masked))
    
    if verbose: print('Mask application:', td(seconds=time.time()-start)); start = time.time()
        
    # Mengembalikan sinyal audio kedalam bentuk time series
    recovered_signal = _istft(sig_stft_amp, hop_length, win_length)
    recovered_spec = _amp_to_db(np.abs(_stft(recovered_signal, n_fft, hop_length, win_length)))
    
    if verbose: print('Signal recovery:', td(seconds=time.time()-start));
    if visual: plot_spectrogram(noise_stft_db, title='Noise')
    if visual: plot_statistics_and_filter(mean_freq_noise, std_freq_noise, noise_thresh, smoothing_filter)
    if visual: plot_spectrogram(sig_stft_db, title='Signal')
    if visual: plot_spectrogram(sig_mask, title='Mask applied')
    if visual: plot_spectrogram(sig_stft_db_masked, title='Masked signal')
    if visual: plot_spectrogram(recovered_spec, title='Recovered spectrogram')
    
    return recovered_signal


def butter_bandpass_filter(audio, low_cut, high_cut, sr, order=1):
    """
    Band pass filter

    Parameter
    ----------
    audio : numpy array
        array sinyal audio
    sr : int
        samplerate dari audio
    low_cut : int
        threshold bawah
    high_cut : int
        threshold atas
    order : int
        roll off band pass
    """
    nyq = 0.5 * sr
    low = low_cut / nyq
    high = high_cut / nyq

    b, a = butter(order, [low, high], btype='band')
    y = lfilter(b, a, audio)

    return y


def get_noise(audio, start_time, end_time, sr=8000):
    """
    Mengambil bagian audio dari waktu start_time sampai end_time

    Parameter
    ----------
    audio : numpy array
        array sinyal audio
    start_time : int
        waktu awal noise pada audio
    end_time : int
        waktu akhir noise pada audio
    sr : int
        samplerate dari audio
    """
    noise = audio[int(sr*start_time):int(sr*end_time)]

    return noise
