import sys
import psutil
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import QTimer, QCoreApplication


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = 'System Monitor'
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(10, 10, 400, 200)
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
        self.tab1.layout.addWidget(self.label)
        self.tab1.setLayout(self.tab1.layout)

        # Add tabs to widget
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

        # Create timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_info)
        self.timer.start(1000)

    def update_info(self):
        cpu_usage = psutil.cpu_percent()
        ram_usage = psutil.virtual_memory().percent
        disk_usage = psutil.disk_usage('/').percent

        net_io_counters = psutil.net_io_counters()
        net_sent = net_io_counters.bytes_sent
        net_recv = net_io_counters.bytes_recv

        processes = [proc.info['name'] for proc in psutil.process_iter(['name'])]

        self.label.setText(f'CPU Usage: {cpu_usage}%\n'
                           f'RAM Usage: {ram_usage}%\n'
                           f'Disk Usage: {disk_usage}%\n'
                           f'Network Usage: Sent {net_sent} bytes / Received {net_recv} bytes\n'
                           f'Running Processes: {processes}\n')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
