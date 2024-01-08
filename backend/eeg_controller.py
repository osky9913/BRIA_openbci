from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
import asyncio
import data_processing
from config import BOARD, SERIAL_PORT, AWS, AWS_TOKEN, AWS_ENDPOINT



# Global buffer for EEG data
eeg_data_buffer = []
global_board = None



async def start_streaming():
    if global_board is not None:
        global_board.start_stream()
        return global_board

async def prepare_eeg_stream(serial_port):
    global global_board
    if global_board is None:
        params = BrainFlowInputParams()
        if BOARD != BoardIds.SYNTHETIC_BOARD:
            params.serial_port = serial_port
        global_board = BoardShim(BOARD, params)
        global_board.prepare_session()
    return global_board



async def get_real_time_eeg_data(ica=False):
    # Fetch real-time data
    if global_board and global_board.is_prepared():
        data = global_board.get_current_board_data(125)  # Get the latest 250 samples, for example
        processed_data = process_eeg_data(data,ica)
        eeg_data_buffer.append(processed_data )
        if eeg_data_buffer:
            return eeg_data_buffer.pop(0)
    return None

def process_eeg_data(data,ica):
    return data_processing.process_data(data,ica)
