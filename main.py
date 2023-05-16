import tkinter as tk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import psutil
import time
import threading


class Monitor:
    def __init__(self):
        self.root = tk.Tk()
        self.fig = Figure(figsize=(10, 8), dpi=100)
        self.cpu_plot = self.fig.add_subplot(221)
        self.mem_plot = self.fig.add_subplot(222)
        self.disk_plot = self.fig.add_subplot(223)
        self.net_plot = self.fig.add_subplot(224)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.update_plots()

    def update_plots(self):
        self.cpu_plot.cla()
        self.cpu_plot.set_title('CPU usage (%)')
        self.cpu_plot.plot(psutil.cpu_percent(interval=1, percpu=True))
        self.cpu_plot.set_ylim(0, 100)

        self.mem_plot.cla()
        self.mem_plot.set_title('Memory usage (%)')
        self.mem_plot.plot(psutil.virtual_memory().percent)
        self.mem_plot.set_ylim(0, 100)

        self.disk_plot.cla()
        self.disk_plot.set_title('Disk usage (%)')
        self.disk_plot.plot(psutil.disk_usage('/').percent)
        self.disk_plot.set_ylim(0, 100)

        self.net_plot.cla()
        self.net_plot.set_title('Network usage (Bytes sent/received)')
        net_io = psutil.net_io_counters()
        self.net_plot.plot([net_io.bytes_sent, net_io.bytes_recv])

        self.canvas.draw()
        self.root.after(1000, self.update_plots)  # refresh every 1s

    def run(self):
        tk.mainloop()


if __name__ == "__main__":
    monitor = Monitor()
    monitor.run()
