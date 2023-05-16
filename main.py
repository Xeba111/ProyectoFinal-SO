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
        self.mem_text = self.fig.text(0.5, 0.7, '', fontsize=12)
        self.disk_text = self.fig.text(0.5, 0.3, '', fontsize=12)
        self.net_plot = self.fig.add_subplot(224)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.cpu_values = []
        self.update_plots()

    def update_plots(self):
        self.cpu_plot.cla()
        self.cpu_plot.set_title('CPU usage (%)')
        cpu_percent = psutil.cpu_percent(interval=1)
        self.cpu_values.append(cpu_percent)
        self.cpu_plot.plot(self.cpu_values, 'r-')
        self.cpu_plot.set_ylim(0, 100)

        self.mem_text.set_text('Memory usage: {:.2f} %'.format(psutil.virtual_memory().percent))

        self.disk_text.set_text('Disk usage: {:.2f} %'.format(psutil.disk_usage('/').percent))

        self.net_plot.cla()
        self.net_plot.set_title('Network usage (Bytes sent/received)')
        net_io = psutil.net_io_counters()
        self.net_plot.plot([net_io.bytes_sent, net_io.bytes_recv], 'b-')

        self.canvas.draw()
        self.root.after(1000, self.update_plots)  # refresh every 1s

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    monitor = Monitor()
    monitor.run()
