import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import psutil
import time
import threading
import pandas as pd
from pandastable import Table

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

        self.processes_frame = ttk.Frame(self.root)
        self.processes_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.update_plots()
        self.update_processes()

    def update_plots(self):
        self.cpu_plot.cla()
        self.cpu_plot.set_title('CPU usage (%)')
        self.cpu_plot.plot(psutil.cpu_percent(interval=1, percpu=True))
        self.cpu_plot.set_ylim(0, 100)

        self.mem_plot.cla()
        self.mem_plot.set_title('Memory usage (%)')
        mem_usage = psutil.virtual_memory().percent
        self.mem_plot.bar(0, mem_usage)
        self.mem_plot.set_ylim(0, 100)
        self.mem_plot.text(0, mem_usage + 1, f'{mem_usage:.2f}%', ha='center', va='bottom')

        self.disk_plot.cla()
        self.disk_plot.set_title('Disk usage (%)')
        disk_usage = psutil.disk_usage('/').percent
        self.disk_plot.bar(0, disk_usage)
        self.disk_plot.set_ylim(0, 100)
        self.disk_plot.text(0, disk_usage + 1, f'{disk_usage:.2f}%', ha='center', va='bottom')

        self.net_plot.cla()
        self.net_plot.set_title('Network usage (Bytes sent/received)')
        net_io = psutil.net_io_counters()
        self.net_plot.bar([0, 1], [net_io.bytes_sent, net_io.bytes_recv])
        self.net_plot.set_xticks([0, 1])
        self.net_plot.set_xticklabels(['Sent', 'Received'])

        self.canvas.draw()
        self.root.after(1000, self.update_plots)

    def update_processes(self):
        process_list = []

        for proc in psutil.process_iter(['pid', 'name', 'status', 'memory_info', 'io_counters']):
            try:
                pid = proc.info['pid']
                name = proc.info['name']
                status = proc.info['status']
                mem_info = proc.info['memory_info'].rss
                io_counters = proc.info['io_counters']
                disk_usage = io_counters.read_bytes + io_counters.write_bytes
                process_list.append([name, pid, status, mem_info, disk_usage])
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass

        process_df = pd.DataFrame(process_list, columns=['Name', 'PID', 'Status', 'Memory usage (Bytes)', 'Disk usage (Bytes)'])
        self.processes_frame.destroy()
        self.processes_frame = ttk.Frame(self.root)
        self.processes_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.table = pt = Table(self.processes_frame, dataframe=process_df)
        pt.show()
        self.root.after(1000, self.update_processes)

def run(self):
    tk.mainloop()

if __name__ == "__main__":
    monitor = Monitor()
    monitor.run()