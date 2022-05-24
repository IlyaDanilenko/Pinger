from PyQt5 import QtWidgets, QtCore
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QLabel,QVBoxLayout, QScrollArea, QMainWindow
from pyqtgraph import PlotWidget
import pyqtgraph as pg
from threading import Thread
import json, sys, ping3
ping3.EXCEPTIONS = True

SYNC = True # синхронизируются ли пинги

TIME = 1000 # время пинга (в мс)
TIMEOUT = TIME - 200 # время после которого устройство считается недоступным
SCALE = 50 # сколько точек показывается
GREEN_RANGE = 100 # до скольки пинг считатеся целеным (в мс)
YELLOW_RANGE = 300 # до скольки пинг считается желтым (в мс)
# красный все остальные значения времени

GRAPHIC_COLOR = (0, 0, 0) # цвет графика (R, G, B)
GRAPHIC_WIDTH = 5 # толщина линии

def get_time_by_ip(ip):
    try:
        return int(ping3.ping(ip, timeout=TIMEOUT * 0.001) * 1000)
    except:
        return None

class Device:
    def __init__(self, name, ip):
        self.name = name
        self.ip = ip

class PingWidget(QWidget):
    def __init__(self, device, screen, count):
        self.__device = device

        size = screen.height() // count // 3

        super().__init__()

        self.setAutoFillBackground(True)
        self.__change_color(QColor(255, 0, 0))

        names_font = QFont('Monospace', int(size * 0.375))
        self.name_label = QLabel(self.__device.name)
        self.name_label.setFont(names_font)
        self.ip_label = QLabel(self.__device.ip.ljust(16))
        self.ip_label.setFont(names_font)

        self.ping_label = QLabel("NA".ljust(4), self)
        self.ping_label.setFont(QFont('Monospace', size))
        self.graph = PlotWidget(self)
        self.graph.setMouseEnabled(False, False)

        self.pen = pg.mkPen(color=GRAPHIC_COLOR, width=GRAPHIC_WIDTH)

        self.x = list(range(SCALE))
        self.y = [0 for _ in range(SCALE)]

        self.graph.setBackground('w')
        self.data_line =  self.graph.plot(self.x, self.y, pen=self.pen)

        self.timer = QtCore.QTimer()
        self.timer.setInterval(TIME)
        self.timer.timeout.connect(self.__timer_handle)
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

    def __timer_handle(self):
        if SYNC:
            self.update_plot_data()
        else:
            Thread(target=self.update_plot_data).start()

    def update_plot_data(self):
        time = get_time_by_ip(self.__device.ip)
        if time is None:
            self.ping_label.setText("NA".ljust(4))
            self.__change_color(QColor(255, 0, 0))
            time = TIMEOUT
        else:
            if time <= GREEN_RANGE:
                self.__change_color(QColor(0, 255, 0))
            elif time <= YELLOW_RANGE:
                self.__change_color(QColor(255, 255, 0))
            self.ping_label.setText(f"{time}".ljust(4))

        self.x = self.x[1:]
        self.x.append(self.x[-1] + 1)

        self.y = self.y[1:]

        self.y.append(time)

        self.data_line.setData(self.x, self.y)

    def __change_color(self, color):
        p = self.palette()
        p.setColor(self.backgroundRole(), color)
        self.setPalette(p)

class MainWindow(QMainWindow):
    def __init__(self, screen, config_file):
        self.__config_file = config_file
        self.__devices = []
        self.__load()
        super().__init__()

        self.setGeometry(screen)

        widget = QWidget()
        widget.setGeometry(screen)

        layout = QVBoxLayout()
        for device in self.__devices:
            deviceWidget = PingWidget(device, screen, len(self.__devices))
            layout.addWidget(deviceWidget)

        widget.setLayout(layout)
        scroll = QScrollArea()
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setWidgetResizable(True)
        scroll.setWidget(widget)

        self.setCentralWidget(scroll)

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()

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