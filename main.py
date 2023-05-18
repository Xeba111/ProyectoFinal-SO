import sys
import threading
import time
import psutil
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QGridLayout, QLabel, QHeaderView, QScrollArea, \
    QTableWidget, QTableWidgetItem
from PyQt5.QtCore import QTimer, QCoreApplication
import pyqtgraph as pg
from PyQt5 import QtCore
import threading

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = 'System Monitor'
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(10, 60, 900, 500)
        self.setMinimumSize(900,500)
        self.setStyleSheet("background-color: #111111; color: #dddddd")
        self.table_widget = MyTableWidget(self)
        self.setCentralWidget(self.table_widget)
        self.table_widget.setStyleSheet(
            "QTabWidget::pane { background-color: white; }"
            "QTabBar::tab { background-color: #240032; border-right: 1px solid grey; padding:5px 100% 5px; }"
            "QTabBar::tab:selected { background-color: #330044; }"
        )
              
        self.show()


class MyTableWidget(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)

        # Initialize tab screen
        self.tabs = QTabWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tab1.setStyleSheet(
            "background-color:#160020; border: 1px solid #333333"
        )
        self.tab2.setStyleSheet(
            "background-color:#160020; border: 1px solid #333333"
        )


        # Add tabs
        self.tabs.addTab(self.tab1, "Processes")
        self.tabs.addTab(self.tab2, "Performance")
        self.tabs.setStyleSheet(
            "QTabWidget::pane:selected { background-color: red; }"  # Selected tab content background color
        ) 

        # Create first tab
        self.tab1.layout = QVBoxLayout(self)
        self.label = QLabel()
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['Name', 'PID', 'RAM (MB)', 'Disk I/O (MB)'])
        self.scroll = QScrollArea()
        self.scroll.setWidget(self.table)
        self.scroll.setWidgetResizable(True)
        self.tab1.layout.addWidget(self.label)
        self.tab1.layout.addWidget(self.scroll)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tab1.setLayout(self.tab1.layout)

        # Create second tab
        self.tab2.layout = QGridLayout(self)
        self.cpu_plot = pg.PlotWidget(title="CPU Usage (%) per Minute")
        self.ram_plot = pg.PlotWidget(title="RAM Usage (%) per Minute")
        self.disk_plot = pg.PlotWidget(title="Disk Usage (%) per Minute")
        self.network_plot = pg.PlotWidget(title="Network Bandwidth Usage (MB) per Minute")

        self.cpu_plot.setMaximumHeight(300)
        self.ram_plot.setMaximumHeight(300)
        self.disk_plot.setMaximumHeight(300)
        self.network_plot.setMaximumHeight(300)

        self.cpu_plot.setYRange(0, 100)
        self.ram_plot.setYRange(0, 100)
        self.disk_plot.setYRange(0, 100)
        self.network_plot.setYRange(0, 100)

        self.cpu_plot.setXRange(-60, 0)
        self.ram_plot.setXRange(-60, 0)
        self.disk_plot.setXRange(-60, 0)
        self.network_plot.setXRange(-60, 0)

        self.cpu_plot.setMouseEnabled(y=False, x=True)
        self.ram_plot.setMouseEnabled(y=False, x=True)
        self.disk_plot.setMouseEnabled(y=False, x=True)
        self.network_plot.setMouseEnabled(y=False, x=True)

        self.cpu_plot.hideButtons()
        self.ram_plot.hideButtons()
        self.disk_plot.hideButtons()
        # self.network_plot.hideButtons()

        def restrictPanning(self, plot_item):
            def onRangeChanged():
                x_range = plot_item.viewRange()[0]
                if x_range[0] < -3600:
                    # Adjust the range if it exceeds the allowed limits
                    plot_item.setXRange(max(x_range[0], -60), min(x_range[1], 0))
                if x_range[1] > 0:
                    # Adjust the range if it exceeds the allowed limits
                    plot_item.setXRange(max(x_range[0], -60), min(x_range[1], 0))

            plot_item.sigRangeChanged.connect(onRangeChanged)

        # Call the restrictPanning method for each plot widget
        restrictPanning(self,self.cpu_plot.plotItem)
        restrictPanning(self,self.ram_plot.plotItem)
        restrictPanning(self,self.disk_plot.plotItem)
        restrictPanning(self,self.network_plot.plotItem)

        self.tab2.layout.addWidget(self.cpu_plot,0,0)
        self.tab2.layout.addWidget(self.ram_plot,0,1)
        self.tab2.layout.addWidget(self.disk_plot,1,0)
        self.tab2.layout.addWidget(self.network_plot,1,1)
        self.tab2.layout.setSpacing(10)
        self.tab2.setLayout(self.tab2.layout)

        # Add tabs to widget
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

        # Create timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_info_thread)
        self.timer.start(1000)

        self.graph_timer = QTimer()
        self.graph_timer.timeout.connect(self.update_graph_thread)
        self.graph_timer.start(1000)

        self.history_length = 3600 // 1  # 1 hour / 30 seconds
        self.cpu_history = [0] * self.history_length
        self.ram_history = [0] * self.history_length
        self.disk_history = [0] * self.history_length
        self.network_sent_history = [0] * self.history_length
        self.network_recv_history = [0] * self.history_length
        self.timestamps = list(range(-self.history_length, 0, 1))

    def bytes_to_mb(self, bytes):
        return bytes / 1024 / 1024

    def update_info(self):
        threading.Thread(target=self.update_info_thread()).start()

    def update_info_thread(self):
        cpu_usage = psutil.cpu_percent()
        ram_usage = psutil.virtual_memory().percent
        disk_usage = psutil.disk_usage('/').percent

        net_io_counters = psutil.net_io_counters()
        net_sent = self.bytes_to_mb(net_io_counters.bytes_sent)
        net_recv = self.bytes_to_mb(net_io_counters.bytes_recv)

        self.table.setRowCount(0)

        for proc in psutil.process_iter(['name', 'pid', 'memory_info', 'io_counters']):
            mem_info = self.bytes_to_mb(proc.info['memory_info'].rss)
            if proc.info['io_counters'] is not None:
                io_info_read = self.bytes_to_mb(proc.info['io_counters'].read_bytes)
                io_info_write = self.bytes_to_mb(proc.info['io_counters'].write_bytes)

                row_position = self.table.rowCount()
                self.table.insertRow(row_position)
                self.table.setItem(row_position, 0, QTableWidgetItem(proc.info["name"]))
                self.table.setItem(row_position, 1, QTableWidgetItem(str(proc.info["pid"])))
                self.table.setItem(row_position, 2, QTableWidgetItem(f'{mem_info:.2f}'))
                self.table.setItem(row_position, 3, QTableWidgetItem(f'{io_info_read:.2f}/{io_info_write:.2f}'))
            else:
            # Handle the case when 'io_counters' is None
                io_info_read = 0  # Or any other appropriate value

            # io_info_read = self.bytes_to_mb(proc.info['io_counters'].read_bytes)
            

            

        self.label.setText(f'CPU Usage: {cpu_usage}%\n'
                           f'RAM Usage: {ram_usage}%\n'
                           f'Disk Usage: {disk_usage}%\n'
                           f'Network Usage: Sent {net_sent:.2f} MB / Received {net_recv:.2f} MB\n')


    def update_graph(self):
        threading.Thread(target=self.update_info_thread()).start()

    def update_graph_thread(self):
        self.cpu_history.append(psutil.cpu_percent())
        self.cpu_history.pop(0)

        self.ram_history.append(psutil.virtual_memory().percent)
        self.ram_history.pop(0)

        self.disk_history.append(psutil.disk_usage('/').percent)
        self.disk_history.pop(0)

        net_io_counters = psutil.net_io_counters()
        net_sent = self.bytes_to_mb(net_io_counters.bytes_sent)
        net_recv = self.bytes_to_mb(net_io_counters.bytes_recv)

        self.network_sent_history.append(net_sent)
        self.network_sent_history.pop(0)

        self.network_recv_history.append(net_recv)
        self.network_recv_history.pop(0)

        self.cpu_plot.plot(self.timestamps, self.cpu_history, clear=True)
        self.ram_plot.plot(self.timestamps, self.ram_history, clear=True)
        self.disk_plot.plot(self.timestamps, self.disk_history, clear=True)
        self.network_plot.plot(self.timestamps, self.network_sent_history, pen='r', name='Sent', clear=True)
        self.network_plot.plot(self.timestamps, self.network_recv_history, pen='b', name='Received')


if __name__ == '__main__':
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_X11InitThreads)
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())