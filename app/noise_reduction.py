import numpy as np
import librosa
import time
import scipy.signal
from datetime import timedelta as td
from scipy.io import wavfile
from pysndfx import AudioEffectsChain

class NoiseReduction:
    
    def _stft(self, y, n_fft, hop_length, win_length):
        
        return librosa.stft(y, n_fft, hop_length, win_length)

    def _istft(self, y, hop_length, win_length):
        
        return librosa.istft(y, hop_length, win_length)

    def _amp_to_db(self, x):
        
        return librosa.core.amplitude_to_db(x, ref=1.0, amin=1e-20, top_db=80.0)

    def _db_to_amp(self, x, ):
        
        return librosa.core.db_to_amplitude(x, ref=1.0)

    def remove_noise(self, audio_clip, noise_clip, n_grad_freq=2, n_grad_time=4, \
        n_fft=2048, win_length=2048, hop_length=512, n_std_thresh=1.5, \
        prop_decrease=1.0, verbose=False, visual=False, debug=False):
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
        noise_stft = self._stft(noise_clip, n_fft, hop_length, win_length)
        noise_stft_db = self._amp_to_db(np.abs(noise_stft))

        # Menghitung statistik pada noise
        mean_freq_noise = np.mean(noise_stft_db, axis=1)
        std_freq_noise = np.std(noise_stft_db, axis=1)
        noise_thresh = mean_freq_noise+std_freq_noise*n_std_thresh

        if verbose:
            print('STFT on noise:', td(seconds=time.time()-start))
            start = time.time()

        # STFT pada sinyal audio
        if verbose: start = time.time()

        sig_stft = self._stft(audio_clip, n_fft, hop_length, win_length)
        sig_stft_db = self._amp_to_db(np.abs(sig_stft))

        if verbose:
            print('STFT on signal:',td(seconds=time.time()-start))
            start = time.time()

        # Menghitung nilai masKing pada desibel
        mask_gain_dB = np.min(self._amp_to_db(np.abs(sig_stft)))
        print(noise_thresh, mask_gain_dB)

        # Membuat filter smoothing untuk masking pada waktu dan frekuensi
        smoothing_filter = np.outer(
            np.concatenate(
                [np.linspace(0, 1, n_grad_freq+1, endpoint=False), np.linspace(1, 0, n_grad_freq+2)])[1:-1], 
            np.concatenate(
                [np.linspace(0, 1, n_grad_time+1, endpoint=False), np.linspace(1, 0, n_grad_time+2)])[1:-1])

        smoothing_filter = smoothing_filter/np.sum(smoothing_filter)

        # Menghitung threshold pada setiap frekuensi/time bin
        db_thresh = np.repeat(
            np.reshape(noise_thresh, [1,len(mean_freq_noise)]), 
            np.shape(sig_stft_db)[1], axis = 0).T

        # Mask apabila sinyal diatas nilai threshold
        sig_mask = sig_stft_db<db_thresh

        if verbose:
            print('Masking:', td(seconds=time.time()-start))
            start = time.time()

        # Convolce mask dengan smoothing filter
        sig_mask = scipy.signal.fftconvolve(sig_mask, smoothing_filter,  mode='same')
        sig_mask = sig_mask*prop_decrease

        if verbose:
            print('Mask convolution:', td(seconds=time.time()-start))
            start = time.time()

        # Mask sinyal audio
        sig_stft_db_masked = sig_stft_db *(1-sig_mask) + np.ones(np.shape(mask_gain_dB))*mask_gain_dB*sig_mask
        sig_imag_masked = np.imag(sig_stft)*(1-sig_mask)
        sig_stft_amp = ((self._db_to_amp(sig_stft_db_masked)*np.sign(sig_stft))+(1j * sig_imag_masked))

        if verbose:
            print('Mask application:', td(seconds=time.time()-start))
            start = time.time()

        # Mengembalikan sinyal audio kedalam bentuk time series
        recovered_signal = self._istft(sig_stft_amp, hop_length, win_length)
        recovered_spec = self._amp_to_db(np.abs(self._stft(recovered_signal, n_fft, hop_length, win_length)))

        if verbose:
            print('Signal recovery:', td(seconds=time.time()-start))

        return recovered_signal

    def reduce_noise_power(self, y, sr):
        """
        Comment
        """
        cent = librosa.feature.spectral_centroid(y, sr)

        threshold_l = round(np.median(cent))*0.1
        threshold_h = round(np.median(cent))*1.5

        less_noise = AudioEffectsChain().lowshelf(gain=-30.0, frequency=threshold_l, slope=0.8) \
            .highshelf(gain=-12.0, frequency=threshold_h, slope=0.5)#.limiter(gain=6.0)
        y_clean = less_noise(y)

        return y_clean