import time
import argparse
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt

from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds

import mne
def main():
    params = BrainFlowInputParams()
    parser = argparse.ArgumentParser()
    parser.add_argument('--serial-port', type=str, help='serial port', required=False, default='')
    args = parser.parse_args()
    params.serial_port = args.serial_port



    
        
    BoardShim.enable_dev_board_logger()
    # use synthetic board for demo
    board = BoardShim(BoardIds.CYTON_DAISY_BOARD, params)
    board.prepare_session()
    board.start_stream()
    time.sleep(10)
    data = board.get_board_data()
    board.stop_stream()
    board.release_session()

    eeg_channels = BoardShim.get_eeg_channels(BoardIds.CYTON_DAISY_BOARD)
    eeg_data = data[eeg_channels, :]
    eeg_data = eeg_data / 1000000  # BrainFlow returns uV, convert to V for MNE

    # Creating MNE objects from brainflow data arrays
    ch_types = ['eeg'] * len(eeg_channels)
    ch_names = BoardShim.get_eeg_names(BoardIds.CYTON_DAISY_BOARD)
    sfreq = BoardShim.get_sampling_rate(BoardIds.CYTON_DAISY_BOARD)
    info = mne.create_info(ch_names=ch_names, sfreq=sfreq, ch_types=ch_types)
    raw = mne.io.RawArray(eeg_data, info)
    # its time to plot something!
    raw.plot_psd(average=True)
    plt.savefig('psd.png')


if __name__ == "__main__":
    main()