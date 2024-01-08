
from brainflow.board_shim import BoardShim, BoardIds
import mne 
import numpy as np
from sklearn.decomposition import FastICA
from scipy.fft import fft
from scipy.signal import welch
from scipy.stats import skew, kurtosis

ch_names = BoardShim.get_eeg_names(BoardIds.CYTON_DAISY_BOARD)
ch_types = ['eeg'] * len(ch_names)
sfreq = BoardShim.get_sampling_rate(BoardIds.CYTON_DAISY_BOARD)
info = mne.create_info(ch_names=ch_names, sfreq=sfreq, ch_types=ch_types)
ICA_C = FastICA(n_components=20, algorithm='parallel', whiten='arbitrary-variance', max_iter=1000, tol=0.01, random_state=0)


def get_info():
    return  { "ch_names": ch_names , "sfreq": sfreq  } 

INFO = get_info()

def process_data(data,ica):
    # Add your data processing logic here
    # For now, it just returns the raw data
    eeg_channels = BoardShim.get_eeg_channels(BoardIds.CYTON_DAISY_BOARD)
    eeg_data = data[eeg_channels, :]
    
    eeg_data = eeg_data / 1000000
    print("eeg_data",eeg_data)
    if ica == True:
        S_ica = ICA_C.fit_transform(eeg_data)
        S_reconstructed = ICA_C.inverse_transform(S_ica) 
        print("S_reconstructed", S_reconstructed)
        eeg_data = S_reconstructed
    return eeg_data.tolist()



def process_data_with_fft(data):
    fft_data = fft(data)
    fft_magnitude = np.abs(fft_data)
    return fft_magnitude.tolist()


