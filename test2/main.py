import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QHBoxLayout
from PyQt5.QtGui import QPixmap, QPalette
from PyQt5.QtCore import Qt

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = 'Qt Application'
        white_palette = QApplication.instance().palette()
        white_palette.setColor(QPalette.Window, Qt.white)
        QApplication.instance().setPalette(white_palette)
        self.initUI()

    def initUI(self):
    # Main window settings
        self.setWindowTitle(self.title)
        self.setGeometry(100, 100, 800, 600)

        # Main layout
        main_layout = QVBoxLayout()
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        central_widget.setLayout(main_layout)


        # Layout for centering the image
        image_layout = QHBoxLayout()
        main_layout.addLayout(image_layout)

        # Create a label for the image
        self.label = QLabel(self)
        pixmap = QPixmap('brain.png')  # Replace 'brain.png' with your image path
        resized_pixmap = pixmap.scaled(400, 400, Qt.KeepAspectRatio)  # Resize the image
        self.label.setPixmap(resized_pixmap)
        self.label.setAlignment(Qt.AlignCenter)  # Center the image

        # Add the label to the layout
        image_layout.addWidget(self.label)

        # Button to get started
        self.button = QPushButton('Get Started', self)
        self.button.clicked.connect(self.on_click)
        main_layout.addWidget(self.button, 0, Qt.AlignCenter)  # Center the button

        # Ensure the image stays centered when resizing the window
        main_layout.addStretch()
    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clear_layout(item.layout())



    def on_click(self):
        # Clear the current layout
        self.clear_layout(self.centralWidget().layout())

        # Change to the new page
        self.setGraphAndButtonsPage()

    def setGraphAndButtonsPage(self):
        # Create a new layout for the page
        layout = QHBoxLayout()
        self.centralWidget().setLayout(layout)

        # Matplotlib graph on the left
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # Buttons on the right
        button_layout = QVBoxLayout()
        self.time_series_button = QPushButton('Time Series', self)
        self.fft_button = QPushButton('FFT', self)
        self.topomap_button = QPushButton('Topomap Features', self)

        button_layout.addWidget(self.time_series_button)
        button_layout.addWidget(self.fft_button)
        button_layout.addWidget(self.topomap_button)
        layout.addLayout(button_layout)

        # Connect buttons to their functionalities
        self.time_series_button.clicked.connect(self.plot_time_series)
        self.fft_button.clicked.connect(self.plot_fft)
        self.topomap_button.clicked.connect(self.show_topomap_features)

    def plot_time_series(self):
        # Implement the plotting logic for time series
        pass

    def plot_fft(self):
        # Implement the plotting logic for FFT
        pass

    def show_topomap_features(self):
        # Implement the logic to show topomap features
        pass

app = QApplication(sys.argv)
ex = App()
ex.show()
sys.exit(app.exec_())
