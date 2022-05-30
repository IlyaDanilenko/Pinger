from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QVBoxLayout, QLabel,QVBoxLayout, QScrollArea, QMainWindow
from pyqtgraph import PlotWidget, AxisItem, mkPen
from threading import Thread
import json, sys, ping3
from time import sleep, time
ping3.EXCEPTIONS = True

TIME = 1000 # время пинга (в мс)
TIMEOUT = TIME - 200 # время после которого устройство считается недоступным
SCALE = 200 # сколько точек показывается
GREEN_RANGE = 100 # до скольки пинг считатеся целеным (в мс)
YELLOW_RANGE = 300 # до скольки пинг считается желтым (в мс)
# красный все остальные значения времени

GRAPHIC_COLOR = (0, 0, 0) # цвет графика (R, G, B)
GRAPHIC_WIDTH = 5 # толщина линии
SHOW_X_AXIS = False # показывать ли значения по оси X
SCROLL = False # Полоска скрола

class Device:
    def __init__(self, name, ip):
        self.name = name
        self.ip = ip

class PingThread(Thread):
    def __init__(self, ip):
        self.result = TIMEOUT
        self.__run = True
        self.__ip = ip
        super().__init__()

    def run(self):
        while self.__run:
            self.result, delta = self.get_time_by_ip()
            sleep(1 - delta)

    def get_time_by_ip(self):
        start = time()
        try:
            return int(ping3.ping(self.__ip, timeout=TIMEOUT * 0.001) * 1000), time() - start
        except:
            return None, time() - start

    def stop(self):
        self.__run = False

class PingWidget(QWidget):
    def __init__(self, device, screen, count):
        self.__device = device

        self.__count = 0
        self.__sum = 0

        size = screen.height() // count // 3

        super().__init__()

        self.setAutoFillBackground(True)
        self.__change_color(QColor(255, 0, 0))

        names_font = QFont('Monospace', int(size * 0.375))
        self.name_label = QLabel(self.__device.name)
        self.name_label.setFont(names_font)
        self.ip_label = QLabel(self.__device.ip.ljust(16))
        self.ip_label.setFont(names_font)

        self.ping_label = QLabel(self.__get_ping_str("NA", "NA", 3), self)
        self.ping_label.setFont(QFont('Monospace', size))
        self.graph = PlotWidget(self)
        self.graph.setMouseEnabled(False, False)

        self.pen = mkPen(color=GRAPHIC_COLOR, width=GRAPHIC_WIDTH)

        self.x = list(range(SCALE))
        self.y = [0 for _ in range(SCALE)]

        self.graph.setBackground('w')
        if not SHOW_X_AXIS:
            new_axis = {"bottom":AxisItem(orientation='bottom', showValues=False, pen=mkPen(color=GRAPHIC_COLOR, width=3)), "left":self.graph.getPlotItem().getAxis('left')}
            self.graph.getPlotItem().setAxisItems(new_axis)
        self.data_line =  self.graph.plot(self.x, self.y, pen=self.pen)

        self.__ping_thread = PingThread(self.__device.ip)
        self.__ping_thread.start()

        self.timer = QTimer()
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
        Thread(target=self.update_plot_data).start()

    def update_plot_data(self):
        time = self.__ping_thread.result
        if time is None:
            time = TIMEOUT
            self.__sum += time
            self.__count += 1
            self.ping_label.setText(self.__get_ping_str("NA", self.__sum // self.__count, 3))
            self.__change_color(QColor(255, 0, 0))
        else:
            self.__sum += time
            self.__count += 1
            if time <= GREEN_RANGE:
                self.__change_color(QColor(0, 255, 0))
            elif time <= YELLOW_RANGE:
                self.__change_color(QColor(255, 255, 0))
            self.ping_label.setText(self.__get_ping_str(time, self.__sum // self.__count, 3))

        self.x = self.x[1:]
        self.x.append(self.x[-1] + 1)

        self.y = self.y[1:]

        self.y.append(time)

        self.data_line.setData(self.x, self.y)

    def __get_ping_str(self, value1, value2, count):
        return str(value1).ljust(count) + "\\" + str(value2).ljust(count)

    def __change_color(self, color):
        p = self.palette()
        p.setColor(self.backgroundRole(), color)
        self.setPalette(p)

    def zero_mid(self):
        self.__sum = 0
        self.__count = 0

    def close_connection(self):
        self.__ping_thread.stop()

class MainWindow(QMainWindow):
    def __init__(self, screen, config_file):
        self.__config_file = config_file
        self.__devices = []
        self.__devices_widget = []
        self.__screen = screen
        self.__load()

        super().__init__()

        self.setGeometry(self.__screen )

        widget = QWidget()
        widget.setGeometry(self.__screen )

        layout = QVBoxLayout()
        for device in self.__devices:
            self.__devices_widget.append(PingWidget(device, self.__screen , len(self.__devices)))
            layout.addWidget(self.__devices_widget[-1])

        widget.setLayout(layout)

        if SCROLL:
            scroll = QScrollArea()
            scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
            scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            scroll.setWidgetResizable(True)
            scroll.setWidget(widget)

            self.setCentralWidget(scroll)
        else:
            self.setCentralWidget(widget)

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()
            for index in range(len(self.__devices_widget)):
                self.__devices_widget[index].close_connection()
        elif event.key() == Qt.Key_F:
            if self.isFullScreen():
                self.showMaximized()
            else:
                self.showFullScreen()
        elif event.key() == Qt.Key_Z:
            for index in range(len(self.__devices_widget)):
                self.__devices_widget[index].zero_mid()

    def __load(self):
        with open(self.__config_file) as f:
            json_data = json.load(f)
            for obj in json_data:
                self.__devices.append(Device(**obj))
                
if __name__ == '__main__':
    app = QApplication(sys.argv)
    main = MainWindow(app.desktop().screenGeometry(), "config/config.json")
    main.show()
    sys.exit(app.exec_())