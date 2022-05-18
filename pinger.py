from pythonping import ping
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QLabel,QVBoxLayout
from pyqtgraph import PlotWidget
import pyqtgraph as pg
import json, sys

TIME = 1000 # врремя пинга (в мс)
SCALE = 50 # сколько точек показывается
GREEN_RANGE = 100 # до скольки пинг считатеся целеным (в мс)
YELLOW_RANGE = 300 # до скольки пинг считается желтым (в мс)
# красный все остальные значения времени

GRAPHIC_COLOR = (0, 0, 0) # цвет графика (R, G, B)
GRAPHIC_WIDTH = 5 # толщина линии

def get_time_by_ip(ip):
    return int(ping(ip, count=1)._responses[0].time_elapsed_ms)

class Device:
    def __init__(self, name, ip):
        self.name = name
        self.ip = ip

class PingWidget(QWidget):
    def __init__(self, device):
        self.__device = device
        super().__init__()

        self.setAutoFillBackground(True)

        names_font = QFont('Monospace', 30)
        self.name_label = QLabel(self.__device.name)
        self.name_label.setFont(names_font)
        self.ip_label = QLabel(self.__device.ip.ljust(16))
        self.ip_label.setFont(names_font)

        self.ping_label = QLabel("NA".ljust(4), self)
        self.ping_label.setFont(QFont('Monospace', 80))
        self.graph = PlotWidget(self)

        self.pen = pg.mkPen(color=GRAPHIC_COLOR, width=GRAPHIC_WIDTH)

        self.x = list(range(SCALE))
        self.y = [0 for _ in range(SCALE)]

        self.graph.setBackground('w')
        self.data_line =  self.graph.plot(self.x, self.y, pen=self.pen)

        self.timer = QtCore.QTimer()
        self.timer.setInterval(TIME)
        self.timer.timeout.connect(self.update_plot_data)
        self.timer.start()

        main_layout = QGridLayout(self)
        w = QWidget()
        layout = QGridLayout(w)
        w.setLayout(layout)
        w1 = QWidget()
        name_layout = QGridLayout(w1)
        w1.setLayout(name_layout)

        name_layout.addWidget(self.name_label, 0, 0)
        name_layout.addWidget(self.ip_label, 1, 0)

        layout.addWidget(w1, 0, 0)
        layout.addWidget(self.ping_label, 0, 1)

        main_layout.addWidget(w, 0, 0)
        main_layout.addWidget(self.graph, 0, 1)

        self.setLayout(main_layout)
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
            self.ping_label.setText("NA".ljust(4))
        else:
            self.ping_label.setText(f"{time}".ljust(4))

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