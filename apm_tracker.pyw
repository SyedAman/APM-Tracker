import re

from pynput import keyboard, mouse
import time
import os
import threading
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sys

def handle_thread_exception(args):
    print(f"Exception in thread {args.exc_type}", file=sys.stderr)
    print(args.exc_value, file=sys.stderr)
    print(args.exc_traceback, file=sys.stderr)

threading.excepthook = handle_thread_exception

class ApmTracker:
    def __init__(self):
        self.keystrokes = 0
        self.mouse_clicks = 0
        self.start_time = time.time()
        self.effective_actions = 0
        self.time_threshold = 0.2  # 200ms
        self.APM_list = []
        self.EAPM_list = []
        self.cumulative_actions = 0
        self.cumulative_effective_actions = 0
        self.intervals_since_start = -1
        self.canvas = None
        self.previous_action_time = 0
        self.keyboard_listener = keyboard.Listener(on_press=self.on_keyboard_press)
        self.mouse_listener = mouse.Listener(on_click=self.on_mouse_click)
        self.tracking_active = False

    def on_keyboard_press(self, key):
        self.keystrokes += 1
        if self.is_effective_action():
            self.effective_actions += 1

    def on_mouse_click(self, x, y, button, pressed):
        if pressed:
            self.mouse_clicks += 1
            if self.is_effective_action():
                self.effective_actions += 1

    def is_effective_action(self):
        current_time = time.time()
        if current_time - self.previous_action_time > self.time_threshold:
            self.previous_action_time = current_time
            return True
        return False

    def on_reset_all(self):
        self.keystrokes = 0
        self.mouse_clicks = 0
        self.effective_actions = 0
        self.APM_list.clear()
        self.EAPM_list.clear()
        self.cumulative_actions = 0
        self.cumulative_effective_actions = 0
        self.intervals_since_start = -1
        self.start_time = time.time()

        # Cancel the previous timer
        self.root.after_cancel(self.timer_id)

        # Immediately update the display
        self.update_display()

    def close_window(self):
        self.keyboard_listener.stop()
        self.mouse_listener.stop()
        self.root.destroy()

    def draw_graph(self):
        fig, ax = plt.subplots(figsize=(5, 4))
        ax.plot(self.APM_list, label="APM", color='blue', marker='o')
        ax.plot(self.EAPM_list, label="EAPM", color='red', marker='o')
        ax.legend()
        ax.set_xlabel('Time (1min intervals)')
        ax.set_ylabel('Actions per Minute')
        ax.set_title('APM & EAPM Over Time')

        if self.canvas:
            self.canvas.get_tk_widget().destroy()

        self.canvas = FigureCanvasTkAgg(fig, master=self.frame_graph)
        canvas_widget = self.canvas.get_tk_widget()
        canvas_widget.grid(row=0, column=0, padx=10, pady=10)
        self.canvas.draw()
        plt.tight_layout()

    def update_display(self):
        if not self.tracking_active:
            return

        current_APM = self.keystrokes + self.mouse_clicks
        self.APM_list.append(current_APM)

        current_EAPM = self.effective_actions
        self.EAPM_list.append(current_EAPM)

        peak_APM = max(self.APM_list)
        peak_EAPM = max(self.EAPM_list)

        self.cumulative_actions += current_APM
        self.cumulative_effective_actions += current_EAPM
        self.intervals_since_start += 1

        average_APM = self.cumulative_actions / self.intervals_since_start if self.intervals_since_start != 0 else 0
        average_EAPM = self.cumulative_effective_actions / self.intervals_since_start if self.intervals_since_start != 0 else 0

        self.average_apm_label.config(text="APM: {:.2f}".format(average_APM))
        self.current_apm_label.config(text="Current APM: {}".format(current_APM))
        self.peak_apm_label.config(text="Peak APM: {}".format(peak_APM))
        self.average_eapm_label.config(text="EAPM: {:.2f}".format(average_EAPM))
        self.current_eapm_label.config(text="Current EAPM: {}".format(current_EAPM))
        self.peak_eapm_label.config(text="Peak EAPM: {}".format(peak_EAPM))

        self.keystrokes = 0
        self.mouse_clicks = 0
        self.effective_actions = 0
        self.start_time = time.time()

        if self.show_graph_var.get():
            self.draw_graph()

        self.timer_id = self.root.after(60000, self.update_display)

    def toggle_graph(self):
        if self.show_graph_var.get():
            self.frame_graph.grid(row=4, column=0, columnspan=2, padx=10, pady=10)
            self.draw_graph()
        else:
            self.frame_graph.grid_remove()
            if self.canvas:
                self.canvas.get_tk_widget().destroy()
                self.canvas = None

    def start_gui(self):
        self.root = tk.Tk()
        self.root.title("APM Tracker")
        self.root.geometry("550x650")
        self.root.resizable(False, False)
        self.root.attributes("-topmost", True)
        self.root.lift()
        self.root.protocol("WM_DELETE_WINDOW", self.close_window)

        font_style_bold = ("Arial", 12, "bold")
        font_style_regular = ("Arial", 10, "italic")

        self.average_apm_label = tk.Label(self.root, text="APM: 0.00", font=font_style_bold)
        self.average_apm_label.grid(row=0, column=0, padx=20, pady=(10, 0))

        self.current_apm_label = tk.Label(self.root, text="Current APM: 0", font=font_style_regular)
        self.current_apm_label.grid(row=1, column=0, padx=20, pady=(10, 0))

        self.peak_apm_label = tk.Label(self.root, text="Peak APM: N/A", font=font_style_regular)
        self.peak_apm_label.grid(row=2, column=0, padx=20, pady=10)

        self.average_eapm_label = tk.Label(self.root, text="EAPM: 0.00", font=font_style_bold)
        self.average_eapm_label.grid(row=0, column=1, padx=20, pady=(10, 0))

        self.current_eapm_label = tk.Label(self.root, text="Current EAPM: 0", font=font_style_regular)
        self.current_eapm_label.grid(row=1, column=1, padx=20, pady=(10, 0))

        self.peak_eapm_label = tk.Label(self.root, text="Peak EAPM: N/A", font=font_style_regular)
        self.peak_eapm_label.grid(row=2, column=1, padx=20, pady=10)

        reset_button = tk.Button(self.root, text="Reset", command=self.on_reset_all, padx=5, pady=5)
        reset_button.grid(row=3, column=0, columnspan=2, pady=(0, 20))

        self.show_graph_var = tk.BooleanVar()
        self.show_graph_var.set(True)
        self.graph_checkbutton = tk.Checkbutton(self.root, text="Show Graph", variable=self.show_graph_var, command=self.toggle_graph)
        self.graph_checkbutton.grid(row=5, column=0, columnspan=2)

        self.frame_graph = ttk.Frame(self.root)
        self.frame_graph.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

        self.root.after(0, self.update_display)

        self.root.mainloop()

        if hasattr(self, 'keyboard_listener'):
            self.keyboard_listener.stop()

        if hasattr(self, 'mouse_listener'):
            self.mouse_listener.stop()

    def start_tracking(self):
        # Note: We start the listeners in their own threads so they don't block the main thread
        threading.Thread(target=self.keyboard_listener.start, daemon=True).start()
        threading.Thread(target=self.mouse_listener.start, daemon=True).start()
        self.tracking_active = True
        self.update_display()  # Restart the timer and updates

    def stop_tracking(self):
        if hasattr(self, 'keyboard_listener'):
            self.keyboard_listener.stop()
        if hasattr(self, 'mouse_listener'):
            self.mouse_listener.stop()
        self.tracking_active = False
        self.root.after_cancel(self.timer_id)  # Stop the timer

    @staticmethod
    def follow(file_path):
        """Read new lines from a file."""
        with open(file_path, 'r') as f:
            f.seek(0, 2)  # Go to the end of the file
            while True:
                line = f.readline()
                print(line)
                if not line:
                    time.sleep(1)  # Sleep for a short interval if no new lines
                    continue
                yield line


    def monitor_log_file(self):
        print("Monitoring log file for game start...")
        log_generator = ApmTracker.follow(self.log_file_path)
        end_pattern = re.compile(r"GameObj::ShutdownGameObj")  # New pattern for game shutdown
        tracking_started = False

        for line in log_generator:
            if not tracking_started and self.pattern.search(line):
                print("Match started! Starting APM tracking...")
                self.start_tracking()
                tracking_started = True
            elif tracking_started and end_pattern.search(line):  # Use regex search here
                print("Match ended! Stopping APM tracking...")
                self.stop_tracking()
                break

    def run(self):
        # Start the log monitoring thread first
        threading.Thread(target=self.monitor_log_file, daemon=True).start()

        # Now, start the GUI in the main thread
        self.start_gui()


if __name__ == "__main__":
    # Instantiate the ApmTracker class
    app = ApmTracker()

    # Set the log file path and pattern
    log_file_path = 'C:\\Users\\syedn\\OneDrive\\OneDrive Documents\\My Games\\Company of Heroes 3\\warnings.log'
    pattern = re.compile(r"\bGAME -- Starting mission\b")

    # Set these attributes in the ApmTracker instance so that they can be used inside its methods
    app.log_file_path = log_file_path
    app.pattern = pattern

    # Start the application (This will spawn both the GUI and log monitoring threads)
    app.run()
