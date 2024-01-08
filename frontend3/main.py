#####################################################################################
#                                                                                   #
#                PLOT A LIVE GRAPH IN A PYQT WINDOW                                 #
#                EXAMPLE 1 (modified for extra speed)                               #
#               --------------------------------------                              #
# This code is inspired on:                                                         #
# https://matplotlib.org/3.1.1/gallery/user_interfaces/embedding_in_qt_sgskip.html  #
# and on:                                                                           #
# https://bastibe.de/2013-05-30-speeding-up-matplotlib.html                         #
#                                                                                   #
#####################################################################################

from __future__ import annotations
from typing import *
import sys
import os
from matplotlib.backends.qt_compat import QtCore, QtWidgets
# from PyQt5 import QtWidgets, QtCore
from matplotlib.backends.backend_qt5agg import FigureCanvas
# from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib import pyplot as plt
import matplotlib as mpl
import numpy as np
import requests
import threading
import websocket
import json




class ApplicationWindow(QtWidgets.QMainWindow):
    '''
    The PyQt5 main window.

    '''
    def __init__(self):
        super().__init__()
        # 1. Window settings
        self.setGeometry(300, 300, 1500, 800)
        self.setWindowTitle("Matplotlib live plot in PyQt - example 1 (modified for extra speed)")
        self.frm = QtWidgets.QFrame(self)
        self.frm.setStyleSheet("QWidget { background-color: #eeeeec; }")
        self.lyt = QtWidgets.QVBoxLayout()
        self.frm.setLayout(self.lyt)
        self.h_layout = QtWidgets.QHBoxLayout()
        self.lyt.addLayout(self.h_layout)
        self.eeg_button = QtWidgets.QPushButton("EEG")
        self.eeg_button_ica = QtWidgets.QPushButton("EEG ICA")

        self.eeg_button_fft = QtWidgets.QPushButton("EEG FFT")
        self.features_button = QtWidgets.QPushButton("Features 3D")
        self.btn4 = QtWidgets.QPushButton("Start Record")
        self.btn4.clicked.connect(self.start_recording)

        self.h_layout.addWidget(self.eeg_button)
        self.h_layout.addWidget(self.eeg_button_ica)
        self.h_layout.addWidget(self.eeg_button_fft)
        self.h_layout.addWidget(self.features_button)
        self.h_layout.addWidget(self.btn4)

        self.eeg_button.clicked.connect(self.showEEGCanvas)
        self.eeg_button_fft.clicked.connect(self.showFFTCanvas)
        self.features_button.clicked.connect(self.showEEGICACANVAS)
        self.features_button.clicked.connect(self.showFeaturesCanvas)



        self.setCentralWidget(self.frm)
        self.channels = []
        # 2. Place the matplotlib figure
        self.myFig = MyFigureCanvas2(x_len=125*5, y_range=[-10, 10], interval=1,num_lines=16)
        self.currentCanvas = self.myFig
        self.lyt.addWidget(self.currentCanvas)
 


        # 3. Show
        self.show()
        return
    
    def switchCanvas(self, newCanvas):
        if self.currentCanvas is not None:
            # Stop the timer or any updates on the current canvas
            self.currentCanvas.stop_updates()  # You need to implement this method in MyFigureCanvas2

            # Remove the widget and explicitly delete it
            self.lyt.removeWidget(self.currentCanvas)
            self.currentCanvas.deleteLater()
            self.currentCanvas = None  # Clear the reference

        # Add the new canvas
        self.currentCanvas = newCanvas
        self.lyt.addWidget(self.currentCanvas)
    
    def showEEGCanvas(self):
        eegCanvas = MyFigureCanvas2(x_len=125*5, y_range=[-10, 10], interval=1,num_lines=16)
        self.switchCanvas(eegCanvas)

    def showEEGICACANVAS(self):
        eegICACanvas = MyFigureCanvas2(x_len=125*5, y_range=[-10, 10], interval=1,num_lines=16)
        self.switchCanvas(eegICACanvas)

    def showFFTCanvas(self):
        fftCanvas =MyFigureCanvas2(x_len=125*1, y_range=[-10, 10], interval=1,num_lines=16) # Initialize with necessary parameters
        self.switchCanvas(fftCanvas)

    def showFeaturesCanvas(self):
        featuresCanvas =MyFigureCanvas2(x_len=125*1, y_range=[-10, 10], interval=1,num_lines=16) # Initialize with necessary parameters
        self.switchCanvas(featuresCanvas)
    
    def start_recording(self):
        try:
            self.channels = json.loads(requests.get("http://localhost:8000/get_info").text)["ch_names"]
            print(self.channels)
            response = requests.get("http://localhost:8000/prepare_stream")
            print(response.text)  # Or handle the response as needed
            threading.Thread(target=self.init_websocket).start()
    
        except Exception as e:
            print("Error making GET request:", e)

    def init_websocket(self):
        print("init_websocket")
        self.websocket = websocket.WebSocketApp("ws://localhost:8000/ws",
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close)

        self.websocket.on_open = self.on_open
        self.websocket.run_forever()

    def on_message(self, ws, message):
        
        data = np.array(json.loads(message))
        if data.shape[1] == 125:
            self.myFig.updateAllData(data) 
        else:
            print("Shape doesnt match")
    def on_error(self, ws, error):
        print(error)

    def on_close(self, ws, close_status_code, close_msg):
        print("### WebSocket closed ###")

    def on_open(self, ws):
        print("WebSocket opened")
    


class MyFigureCanvas2(FigureCanvas):
    def __init__(self, x_len:int, y_range:List, interval:int, num_lines:int = 16,ch_names=[
    "Fp1",
    "Fp2",
    "C3",
    "C4",
    "P7",
    "P8",
    "O1",
    "O2",
    "F7",
    "F8",
    "F3",
    "F4",
    "T7",
    "T8",
    "P3",
    "P4"
  ],) -> None:
        super().__init__(plt.figure())
        self._x_len_ = x_len
        self._y_range_ = y_range
        self._num_lines = num_lines

        self._x_ = list(range(0, x_len))
        self._lines_ = []
        self.allData = np.zeros((16, 1))
        line_spacing = 5
        self._y_offsets = [line_spacing * i for i in range(num_lines)]

        
        self._ax_ = self.figure.subplots()
        self._ax_.set_ylim(ymin=-1, ymax=1 + line_spacing * num_lines)
        self._ax_.legend(ch_names)

        self._ax_.set_yticks(self._y_offsets)
        
        self._ax_.set_yticklabels(ch_names)

        # Initialize lines and their corresponding y data
        for _ in range(self._num_lines):
            y = [0] * x_len
            line, = self._ax_.plot(self._x_, y)
            self._lines_.append({'line': line, 'y_data': y})

        self.draw()
        
        self._timer_ = self.new_timer(interval, [(self._update_canvas_, (), {})])
        self._timer_.start()
        

    def updateAllData(self,newData):
        self.allData = np.hstack ((self.allData,10000*newData))

    def get_next_datapoint(self):
        if self.allData.shape[1] == 0:
            return None
        # Determine the number of columns to retrieve (up to 125)
        num_cols_to_retrieve = min(1, self.allData.shape[1])
        
        # Retrieve the first num_cols_to_retrieve columns
        next_point = self.allData[:, 0:num_cols_to_retrieve]

        # Remove the retrieved columns from data
        self.allData = self.allData[:, num_cols_to_retrieve:]

        return next_point
    
    def stop_updates(self):
        # Stop the timer if it exists
        if hasattr(self, '_timer_'):
            self._timer_.stop()


    def _update_canvas_(self) -> None:
        if self.allData.shape[0] >= 16 and self.allData.shape[1] > 2 :
            new_data_points = self.get_next_datapoint()
            print(new_data_points.shape)
            if type(new_data_points) == None:
                return  # Retrieve the next set of data points
            for i, new_data in enumerate(new_data_points):
                print(new_data)
                print( len(self._lines_[i]['y_data']))
                self._lines_[i]['y_data'].extend( list(self._y_offsets[i]+new_data))
                self._lines_[i]['y_data'] = self._lines_[i]['y_data'][-self._x_len_:]
                self._lines_[i]['line'].set_ydata(self._lines_[i]['y_data'])

            self.draw()
            self.flush_events()



def extract_bci_features(eeg_data, sfreq):
    # Assuming eeg_data is a 2D array of shape (n_channels, n_samples)
    features = []

    # Frequency bands
    bands = {'Delta': (0.5, 4), 'Theta': (4, 8), 'Alpha': (8, 13), 'Beta': (13, 30), 'Gamma': (30, 100)}

    for channel_data in eeg_data:
        # Band power features
        for band in bands.values():
            power = band_power(channel_data, sfreq, band)
            features.append(power)

        # Statistical features
        features.append(np.mean(channel_data))
        features.append(np.std(channel_data))
        features.append(np.var(channel_data))
        features.append(skew(channel_data))
        features.append(kurtosis(channel_data))

    return features

if __name__ == "__main__":
    qapp = QtWidgets.QApplication(sys.argv)
    app = ApplicationWindow()
    qapp.exec_()