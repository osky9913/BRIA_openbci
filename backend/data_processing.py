
from brainflow.board_shim import BoardShim, BoardIds
import mne 
import numpy as np



def get_info():
    ch_names = BoardShim.get_eeg_names(BoardIds.CYTON_DAISY_BOARD)
    ch_types = ['eeg'] * len(ch_names)
    sfreq = BoardShim.get_sampling_rate(BoardIds.CYTON_DAISY_BOARD)
    info = mne.create_info(ch_names=ch_names, sfreq=sfreq, ch_types=ch_types)
    return  { "ch_names": ch_names , "sfreq": sfreq  } 

INFO = get_info()

def process_data(data):
    # Add your data processing logic here
    # For now, it just returns the raw data
    eeg_channels = BoardShim.get_eeg_channels(BoardIds.CYTON_DAISY_BOARD)
    eeg_data = data[eeg_channels, :]
    
    eeg_data = eeg_data / 1000000 


    
    
    return eeg_data.tolist()


