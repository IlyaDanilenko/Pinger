from pythonping import ping
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QLabel, QListWidget, QListWidgetItem
from pyqtgraph import PlotWidget
import pyqtgraph as pg
import json, sys

FONT_SIZE = 40 # размер шрифта
TIME = 1000 # врремя пинга (в мс)
SCALE = 50 # сколько точек показывается
GREEN_RANGE = 100 # до скольки пинг считатеся целеным (в мс)
YELLOW_RANGE = 300 # до скольки пинг считается желтым (в мс)
# красный все остальные значения времени

GRAPHIC_COLOR = (0, 0, 0) # цвет графика (R, G, B)
GRAPHIC_WIDTH = 5 # толщина линии

def get_time_by_ip(ip):
    return round(ping(ip, count=1)._responses[0].time_elapsed_ms, 3)

class Device:
    def __init__(self, name, ip):
        self.name = name
        self.ip = ip

class PingWidget(QWidget):
    def __init__(self, device):
        self.__device = device
        super().__init__()

        self.setAutoFillBackground(True)

        self.__font = QFont('Times', FONT_SIZE)
        self.__widgets = [
            QLabel(self.__device.name),
            QLabel(self.__device.ip),
            QLabel("NA", self),
            PlotWidget(self)
        ]

        self.pen = pg.mkPen(color=GRAPHIC_COLOR, width=GRAPHIC_WIDTH)

        self.x = list(range(SCALE))
        self.y = [0 for _ in range(SCALE)]

        self.__widgets[-1].setBackground('w')
        self.data_line =  self.__widgets[-1].plot(self.x, self.y, pen=self.pen)

        self.timer = QtCore.QTimer()
        self.timer.setInterval(TIME)
        self.timer.timeout.connect(self.update_plot_data)
        self.timer.start()

        layout = QGridLayout(self)

        positions = [(i,j) for i in range(1) for j in range(4)]

        layout.setRowStretch(0, 1)
        for position, widget in zip(positions, self.__widgets):
            widget.setFont(self.__font)
            layout.addWidget(widget, *position)
            layout.setColumnStretch(positions.index(position), 1)
        self.setLayout(layout)
        self.show()

    def update_plot_data(self):
        self.x = self.x[1:]
        self.x.append(self.x[-1] + 1)

        self.y = self.y[1:]

        time = get_time_by_ip(self.__device.ip)
        if time <= GREEN_RANGE:
            self.__change_color(QColor(0, 255, 0))
        elif time <= YELLOW_RANGE:
            self.__change_color(QColor(255, 255, 0))
        else:
            self.__change_color(QColor(255, 0, 0))
        self.y.append(time)

        if time == 2000:
            self.__widgets[-2].setText("NA")
        else:
            self.__widgets[-2].setText(f"{time} ms")

        self.data_line.setData(self.x, self.y)

    def __change_color(self, color):
        p = self.palette()
        p.setColor(self.backgroundRole(), color)
        self.setPalette(p)


class MainWindow(QWidget):
    def __init__(self, screen, config_file):
        self.__config_file = config_file
        self.__devices = []
        self.__load()
        super().__init__()
        self.setGeometry(screen)
        layout = QVBoxLayout()

        for device in self.__devices:
            deviceWidget = PingWidget(device)
            layout.addWidget(deviceWidget)
        self.setLayout(layout)

    def __load(self):
        with open(self.__config_file) as f:
            json_data = json.load(f)
            for obj in json_data:
                self.__devices.append(Device(**obj))
                
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    main = MainWindow(app.desktop().screenGeometry(), "config/config.json")
    main.show()
    sys.exit(app.exec_())