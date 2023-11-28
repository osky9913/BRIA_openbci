from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
import asyncio
import data_processing




# Global buffer for EEG data
eeg_data_buffer = []

async def start_eeg_stream(serial_port):
    params = BrainFlowInputParams()
    params.serial_port = serial_port
    board = BoardShim(BoardIds.CYTON_DAISY_BOARD, params)
    board.prepare_session()
    board.start_stream()
    # Do not fetch data here, just start the stream
    return board  # Return the board object for further use

async def get_real_time_eeg_data(board):
    # Fetch real-time data
    if board.is_prepared():
        data = board.get_board_data()  # Get the latest 250 samples, for example
        processed_data = process_eeg_data(data)
        eeg_data_buffer.append(processed_data )
        if eeg_data_buffer:
            return eeg_data_buffer.pop(0)
    return None

def process_eeg_data(data):
    return data_processing.process_data(data)
