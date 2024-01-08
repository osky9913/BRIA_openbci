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
from sklearn.decomposition import PCA
import websocket
import json
import qdarktheme
from mne_features.feature_extraction import extract_features

from scipy.signal import welch
from scipy.stats import skew, kurtosis

FLAG_CURRENT_CANVAS = "EEG"
STREAM_STARTED = False


class ApplicationWindow(QtWidgets.QMainWindow):
    '''
    The PyQt5 main window.

    '''
    def __init__(self):
        super().__init__()
        # 1. Window settings
        self.setGeometry(300, 300, 1500, 800)
        self.setWindowTitle("Matplotlib live plot in PyQt - example 1 (modified for extra speed)")
        self.all_eeg_data = np.zeros((16, 1))
        self.all_ica_data = np.zeros((16, 1))
        self.all_fft_data = np.zeros((16, 1))
        self.all_features_data = np.zeros((16, 1))
        self.all_feature_data_transform = np.zeros((1, 80))



        self.frm = QtWidgets.QFrame(self)
        self.lyt = QtWidgets.QVBoxLayout()
        self.frm.setLayout(self.lyt)
        self.h_layout = QtWidgets.QHBoxLayout()
        self.lyt.addLayout(self.h_layout)




        self.eeg_button = QtWidgets.QPushButton("EEG")
        self.eeg_button.clicked.connect(self.showEEGCanvas)

        self.eeg_button_ica = QtWidgets.QPushButton("EEG ICA")
        self.eeg_button_ica.clicked.connect(self.showEEGICACANVAS)

        self.eeg_button_fft = QtWidgets.QPushButton("EEG FFT")
        self.eeg_button_fft.clicked.connect(self.showFFTCanvas)

        self.features_button = QtWidgets.QPushButton("Features 3D")
        self.features_button.clicked.connect(self.showFeaturesCanvas)

        self.btn4 = QtWidgets.QPushButton("Start Record")
        self.btn4.clicked.connect(lambda: self.start_recording("ws://localhost:8000/ws"))

        self.h_layout.addWidget(self.eeg_button)
        self.h_layout.addWidget(self.eeg_button_ica)
        self.h_layout.addWidget(self.eeg_button_fft)
        self.h_layout.addWidget(self.features_button)
        self.h_layout.addWidget(self.btn4)




        self.setCentralWidget(self.frm)
        self.channels = []
        # 2. Place the matplotlib figure
        self.eeg_canvas = self.EegFigureCanvas(self,x_len=125*5, y_range=[-10, 10], interval=1,num_lines=16)
        self.ica_canvas = self.EegFigureCanvas(self,x_len=125*5, y_range=[-10, 10], interval=1,num_lines=16)

        self.fft_canvas = self.EegFFTFigureCanvas(self,x_len=125, interval=1,num_lines=16)
        self.features_canvas = self.EegFigureCanvasPCA(self, interval=1)

        self.lyt.addWidget(self.eeg_canvas)
        self.eeg_canvas.hide()
        self.lyt.addWidget(self.fft_canvas)
        self.fft_canvas.hide()
        self.lyt.addWidget(self.ica_canvas)
        self.ica_canvas.hide()
        self.lyt.addWidget(self.features_canvas)
        self.features_canvas.hide()

        self.currentCanvas = self.eeg_canvas
        self.currentCanvas.show()


        self.show()
        return
    
    def update_eeg_data(self,newData):
        self.all_eeg_data = np.hstack ((self.all_eeg_data,10000*newData))

    def update_ica_data(self,newData):
        self.all_ica_data = np.hstack ((self.all_ica_data,10000*newData))
    
    def update_fft_data(self,newData):
        self.all_fft_data = np.hstack ((self.all_fft_data,10000*newData))
    
    def update_features_data(self,newData):
        self.all_features_data = np.hstack((self.all_features_data,newData))

    def switchCanvas(self, newCanvas):
        if self.currentCanvas is not None:
            self.currentCanvas.hide()  # Hide the current canvas

        self.currentCanvas = newCanvas
        self.currentCanvas.show()
    
    def showEEGCanvas(self):
        FLAG_CURRENT_CANVAS = "EEG"
        self.switchCanvas(self.eeg_canvas)
        
        """
        self.lyt.removeWidget(self.currentCanvas)
        self.currentCanvas = self.eeg_canvas
        self.lyt.addWidget(self.currentCanvas)
        """

    def showEEGICACANVAS(self):
        FLAG_CURRENT_CANVAS = "ICA"     
        self.switchCanvas(self.ica_canvas)

        """
        self.lyt.removeWidget(self.currentCanvas)
        self.currentCanvas = self.ica_canvas
        self.lyt.addWidget(self.currentCanvas)
        """

    def showFFTCanvas(self):
        FLAG_CURRENT_CANVAS = "FFT"
        self.switchCanvas(self.fft_canvas)

        
        """
        self.lyt.removeWidget(self.currentCanvas)
        self.currentCanvas = self.fft_canvas
        self.lyt.addWidget(self.currentCanvas)
        """

    
    def showFeaturesCanvas(self):
        FLAG_CURRENT_CANVAS = "FEATURES"
        self.switchCanvas(self.features_canvas)
        
    def start_recording(self,url="ws://localhost:8000/ws"):
        print("Starting recording")
        print(url)
        global STREAM_STARTED
        try:
            self.channels = json.loads(requests.get("http://localhost:8000/get_info").text)["ch_names"]
            print(self.channels)
            if STREAM_STARTED == False:
                response = requests.get("http://localhost:8000/prepare_stream")
                print(response.text)  # Or handle the response as needed
                STREAM_STARTED = True

            threading.Thread(target=self.init_websocket_eeg).start()
            threading.Thread(target=self.init_websocket_fft).start()
            threading.Thread(target=self.init_websocket_ica).start()


    
        except Exception as e:
            print("Error making GET request:", e)

    def init_websocket_eeg(self):
        print("Initializing eeg WebSocket")
        self.websocket = websocket.WebSocketApp("ws://localhost:8000/ws",
                                                on_message=self.on_message_eeg,
                                                on_error=self.on_error,
                                                on_close=self.on_close)

        self.websocket.on_open = self.on_open
        self.websocket.run_forever()

    def init_websocket_ica(self):
        print("Initializing ica WebSocket")
        self.websocket = websocket.WebSocketApp("ws://localhost:8000/ica",
                                                on_message=self.on_message_ica,
                                                on_error=self.on_error,
                                                on_close=self.on_close)

        self.websocket.on_open = self.on_open
        self.websocket.run_forever()

    def init_websocket_fft(self):
        print("Initializing ica WebSocket")
        self.websocket = websocket.WebSocketApp("ws://localhost:8000/fft",
                                                on_message=self.on_message_fft,
                                                on_error=self.on_error,
                                                on_close=self.on_close)

        self.websocket.on_open = self.on_open
        self.websocket.run_forever()    

    """
    def init_websocket(self, url):
        print("Initializing WebSocket with URL:", url)
        self.websocket = websocket.WebSocketApp(url,
                                                on_message=self.on_message,
                                                on_error=self.on_error,
                                                on_close=self.on_close)

        self.websocket.on_open = self.on_open
        self.websocket.run_forever()
    """


    def on_message_eeg(self, ws, message):
        data = np.array(json.loads(message))
        if data.shape[1] == 125:
            self.update_eeg_data(data) 
            self.update_features_data(data)
        else:
            print("Shape doesnt match")
            print(data.shape)

    def on_message_ica(self, ws, message):
        data = np.array(json.loads(message))
        if data.shape[1] == 125:
            self.update_ica_data(data) 
        else:
            print("Shape doesnt match")
            print(data.shape)

    def on_message_fft(self, ws, message):
        data = np.array(json.loads(message))
        if data.shape[1] == 125:
            self.update_fft_data(data) 
        else:
            print("Shape doesnt match")
            print(data.shape)

    def on_message_features(self, ws, message):
        data = np.array(json.loads(message))
        if data.shape[1] == 125:
            self.update_features_data(data) 
        else:
            print("Shape doesnt match")
            print(data.shape)
            

    """
    def on_message(self, ws, message):
        
        data = np.array(json.loads(message))
        if data.shape[1] == 125:
            self.currentCanvas.updateAllData(data) 
        else:
            print("Shape doesnt match")
            print(data.shape)
    """
    def on_error(self, ws, error):
        print(error)

    def on_close(self, ws, close_status_code, close_msg):
        print("### WebSocket closed ###")

    def on_open(self, ws):
        print("WebSocket opened")
    


    class EegFigureCanvas(FigureCanvas):
        def __init__(self,parent, x_len:int, y_range:List, interval:int, num_lines:int = 16,ch_names=[
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
            self.parent = parent
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
            self.parent.all_eeg_data = np.hstack ((self.parent.all_eeg_data,10000*newData))

        def get_next_datapoint(self):
            if self.parent.all_eeg_data.shape[1] == 0:
                return None
            # Determine the number of columns to retrieve (up to 125)
            num_cols_to_retrieve = min(1, self.parent.all_eeg_data.shape[1])
            
            # Retrieve the first num_cols_to_retrieve columns
            next_point = self.parent.all_eeg_data[:, 0:num_cols_to_retrieve]

            # Remove the retrieved columns from data
            self.parent.all_eeg_data = self.parent.all_eeg_data[:, num_cols_to_retrieve:]

            return next_point
        
        def stop_updates(self):
            # Stop the timer if it exists
            if hasattr(self, '_timer_'):
                self._timer_.stop()


        def _update_canvas_(self) -> None:
            if self.parent.all_eeg_data.shape[0] >= 16 and self.parent.all_eeg_data.shape[1] > 2 :
                new_data_points = self.get_next_datapoint()
                if type(new_data_points) == None:
                    return  # Retrieve the next set of data points
                for i, new_data in enumerate(new_data_points):
                    self._lines_[i]['y_data'].extend( list(self._y_offsets[i]+new_data))
                    self._lines_[i]['y_data'] = self._lines_[i]['y_data'][-self._x_len_:]
                    self._lines_[i]['line'].set_ydata(self._lines_[i]['y_data'])

                self.draw()
                self.flush_events()

    class EegFigureCanvasICA(FigureCanvas):
        def __init__(self,parent, x_len:int, y_range:List, interval:int, num_lines:int = 16,ch_names=[
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
            self.parent = parent
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
            

            # Initialize lines and their corresponding y data
            for _ in range(self._num_lines):
                y = [0] * x_len
                line, = self._ax_.plot(self._x_, y)
                self._lines_.append({'line': line, 'y_data': y})

            self.draw()
            
            self._timer_ = self.new_timer(interval, [(self._update_canvas_, (), {})])
            self._timer_.start()
            

        def updateAllData(self,newData):
            self.parent.all_ica_data = np.hstack ((self.parent.all_ica_data,10000*newData))

        def get_next_datapoint(self):
            if self.parent.all_ica_data.shape[1] == 0:
                return None
            # Determine the number of columns to retrieve (up to 125)
            num_cols_to_retrieve = min(1, self.parent.all_ica_data.shape[1])
            
            # Retrieve the first num_cols_to_retrieve columns
            next_point = self.parent.all_ica_data[:, 0:num_cols_to_retrieve]

            # Remove the retrieved columns from data
            self.parent.all_ica_data = self.parent.all_ica_data[:, num_cols_to_retrieve:]

            return next_point
        
        def stop_updates(self):
            # Stop the timer if it exists
            if hasattr(self, '_timer_'):
                self._timer_.stop()


        def _update_canvas_(self) -> None:
            if self.parent.all_ica_data.shape[0] >= 16 and self.parent.all_ica_data.shape[1] > 2 :
                new_data_points = self.get_next_datapoint()
                if type(new_data_points) == None:
                    return  # Retrieve the next set of data points
                for i, new_data in enumerate(new_data_points):
         
                    self._lines_[i]['y_data'].extend( list(self._y_offsets[i]+new_data))
                    self._lines_[i]['y_data'] = self._lines_[i]['y_data'][-self._x_len_:]
                    self._lines_[i]['line'].set_ydata(self._lines_[i]['y_data'])

                self.draw()
                self.flush_events()

    
    class EegFigureCanvasPCA(FigureCanvas):
        def __init__(self, parent, interval: int) -> None:
            super().__init__(plt.figure())
            self.parent = parent
            self.pca = PCA(n_components=3)  # Reduce to 3 dimensions
            self._ax_ = self.figure.add_subplot(111, projection='3d')
            self._timer_ = self.new_timer(interval, [(self._update_canvas_, (), {})])
            self._timer_.start()


        def get_next_datapoint(self):
            if self.parent.all_features_data.shape[1] == 0:
                return None
            # Determine the number of columns to retrieve (up to 125)
            num_cols_to_retrieve = min(1000, self.parent.all_features_data.shape[1])
            
            # Retrieve the first num_cols_to_retrieve columns
            next_point = self.parent.all_features_data[:, 0:num_cols_to_retrieve]

            # Remove the retrieved columns from data
            self.parent.all_features_data = self.parent.all_features_data[:, num_cols_to_retrieve:]

            return next_point


        def _update_canvas_(self) -> None:
            print("Updating canvas")
            print(self.parent.all_features_data.shape)

            
            # Assuming self.parent.all_features_data is your 5D data
            if self.parent.all_features_data.shape[0] >= 16 and self.parent.all_features_data.shape[1] > 1000 :

                next_data_point = self.get_next_datapoint()
                features = extract_bci_features(next_data_point,125)
                print(features)
                print(features.shape)
                self.parent.all_feature_data_transform = np.vstack([self.parent.all_feature_data_transform, features])

            if len(self.parent.all_feature_data_transform) > 5:
                reduced_data = self.pca.fit_transform(self.parent.all_feature_data_transform)
                #self.parent.all_feature_data_transform = self.parent.all_feature_data_transform[1:, :]


                self._ax_.clear()
                self._ax_.scatter(reduced_data[:, 0], reduced_data[:, 1], reduced_data[:, 2])
                self.draw()
                self.flush_events()      


    class EegFFTFigureCanvas(FigureCanvas):
        def __init__(self, parent, x_len: int, interval: int, num_lines: int = 16):
            super().__init__(plt.figure())
            self.parent = parent
            self._x_len_ = x_len
            self._num_lines = num_lines

            self._lines_ = []
            self._ax_ = self.figure.subplots()
            self._ax_.set_ylim(ymin=0, ymax=10)  # Adjust y-axis limits as needed

            # Frequency axis (X-axis)
            self.freqs = np.fft.rfftfreq(x_len, d=1.0 / 1000) # Adjust the sample spacing (d) as needed

            # Initialize lines for each EEG channel
            for _ in range(num_lines):
                line, = self._ax_.plot(self.freqs, np.zeros_like(self.freqs))
                self._lines_.append(line)

            self._timer_ = self.new_timer(interval, [(self._update_canvas_, (), {})])
            self._timer_.start()

        def get_next_datapoint(self):
    
            if self.parent.all_fft_data.shape[1] >= self._x_len_:
                # Extract the last 'self._x_len_' columns for FFT
                next_data_points = self.parent.all_fft_data[:, -self._x_len_:]

                # Optionally, you can remove the extracted data to avoid reprocessing it
                self.parent.all_fft_data = self.parent.all_fft_data[:, :-self._x_len_]

                return next_data_points
            else:
                # Not enough data, return None or handle as needed
                return None
            
        def _update_canvas_(self):
            new_data_points = self.get_next_datapoint()
            if new_data_points is not None:
                for i, channel_data in enumerate(new_data_points):
                    fft_data = np.fft.rfft(channel_data)
                    magnitude = np.abs(fft_data)
                    self._lines_[i].set_ydata(magnitude)
                self.draw()
                self.flush_events()



def extract_bci_features(eeg_data, sfreq):
    selected_funcs = ['mean', 'variance', 'skewness', 'kurtosis', 'line_length']
    features = extract_features(np.array([eeg_data]), sfreq, selected_funcs)

    return features

if __name__ == "__main__":
    qapp = QtWidgets.QApplication(sys.argv)
    qdarktheme.setup_theme()
    plt.style.use('dark_background')

    app = ApplicationWindow()
    qapp.exec_()