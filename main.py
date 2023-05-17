import sys
import psutil
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel, QScrollArea, \
    QTableWidget, QTableWidgetItem
from PyQt5.QtCore import QTimer, QCoreApplication


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = 'System Monitor'
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(10, 10, 400, 600)
        self.table_widget = MyTableWidget(self)
        self.setCentralWidget(self.table_widget)
        self.show()


class MyTableWidget(QWidget):
    def __init__(self, parent):
        super(QWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)

        # Initialize tab screen
        self.tabs = QTabWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tabs.resize(300, 200)

        # Add tabs
        self.tabs.addTab(self.tab1, "Tab 1")
        self.tabs.addTab(self.tab2, "Tab 2")

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
        self.tab1.setLayout(self.tab1.layout)

        # Add tabs to widget
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

        # Create timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_info)
        self.timer.start(1000)

    def bytes_to_mb(self, bytes):
        return bytes / 1024 / 1024

    def update_info(self):
        cpu_usage = psutil.cpu_percent()
        ram_usage = psutil.virtual_memory().percent
        disk_usage = psutil.disk_usage('/').percent

        net_io_counters = psutil.net_io_counters()
        net_sent = self.bytes_to_mb(net_io_counters.bytes_sent)
        net_recv = self.bytes_to_mb(net_io_counters.bytes_recv)

        self.table.setRowCount(0)

        for proc in psutil.process_iter(['name', 'pid', 'memory_info', 'io_counters']):
            mem_info = self.bytes_to_mb(proc.info['memory_info'].rss)
            io_info_read = self.bytes_to_mb(proc.info['io_counters'].read_bytes)
            io_info_write = self.bytes_to_mb(proc.info['io_counters'].write_bytes)

            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            self.table.setItem(row_position, 0, QTableWidgetItem(proc.info["name"]))
            self.table.setItem(row_position, 1, QTableWidgetItem(str(proc.info["pid"])))
            self.table.setItem(row_position, 2, QTableWidgetItem(f'{mem_info:.2f}'))
            self.table.setItem(row_position, 3, QTableWidgetItem(f'{io_info_read:.2f}/{io_info_write:.2f}'))

        self.label.setText(f'CPU Usage: {cpu_usage}%\n'
                           f'RAM Usage: {ram_usage}%\n'
                           f'Disk Usage: {disk_usage}%\n'
                           f'Network Usage: Sent {net_sent:.2f} MB / Received {net_recv:.2f} MB\n')

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
