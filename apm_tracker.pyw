# APM & EAPM tracker by MrSkribb

from pynput import keyboard, mouse
import time
import tkinter as tk

keystrokes = 0
mouse_clicks = 0
start_time = time.time()
effective_actions = 0
time_threshold = 0.2  # 200ms (ideal time as human spam is often not slower than this)
APM_list = []
EAPM_list = []


def on_press(key):  # Keystrokes
    global keystrokes, effective_actions
    keystrokes += 1
    if is_effective_action():
        effective_actions += 1
    print("key")


def on_click(x, y, button, pressed):  # Mouse clicks
    global mouse_clicks, effective_actions
    if pressed:
        mouse_clicks += 1
        if is_effective_action():
            effective_actions += 1
        print("mouse")


def is_effective_action():  # Checks for effective actions (EAPM)
    current_time = time.time()
    previous_action_time = getattr(is_effective_action, "previous_action_time", 0)
    if current_time - previous_action_time > time_threshold:
        is_effective_action.previous_action_time = current_time
        return True
    return False


def calculate_actions_per_minute(actions_count):  # Calculates Actions or Effective Actions Per Minute
    elapsed_time = max(time.time() - start_time, 0.001)  # prevent division by zero
    return (actions_count / elapsed_time) * 60


def on_reset_click():
    global keystrokes, mouse_clicks, effective_actions
    keystrokes = 0
    mouse_clicks = 0
    effective_actions = 0
    APM_list.clear()
    EAPM_list.clear()
    update_display()  # Immediately update the display after resetting


def update_display():
    # Display APM
    APM = round(calculate_actions_per_minute(keystrokes + mouse_clicks))
    apm_label.config(text="APM: {}".format(APM))
    APM_list.append(APM)
    peak_APM = max(APM_list) if APM_list else 0
    peak_apm_label.config(text="Peak APM: {}".format(peak_APM))

    # Display effective APM
    EAPM = round(calculate_actions_per_minute(effective_actions))
    effective_APM_label.config(text="EAPM: {}".format(EAPM))

    # Calculates peak Effective APM
    EAPM_list.append(EAPM)
    peak_EAPM = max(EAPM_list) if EAPM_list else 0
    peak_eapm_label.config(text="Peak EAPM: {}".format(peak_EAPM))

    root.after(30000, update_display)


def start_gui():
    global root, apm_label, peak_apm_label, effective_APM_label, peak_eapm_label, keyboard_listener, mouse_listener

    # Create GUI window
    root = tk.Tk()
    root.title("APM Tracker")
    root.geometry("200x150")
    root.resizable(False, False)
    root.attributes("-topmost", True)
    root.lift()

    font_style_bold = ("Arial", 12, "bold")
    font_style_regular = ("Arial", 10, "italic")

    apm_label = tk.Label(root, text="APM: 0", font=font_style_bold)
    apm_label.pack()

    effective_APM_label = tk.Label(root, text="EAPM: 0", font=font_style_bold)
    effective_APM_label.pack()

    peak_apm_label = tk.Label(root, text="Peak APM: N/A", font=font_style_regular)
    peak_apm_label.pack()

    peak_eapm_label = tk.Label(root, text="Peak EAPM: N/A", font=font_style_regular)
    peak_eapm_label.pack(pady=(0, 10))  # Added padding at the bottom

    reset_button = tk.Button(root, text="Reset", command=on_reset_click, padx=5, pady=5)
    reset_button.pack()

    root.after(0, update_display)
    root.mainloop()

    # Stop listeners and exit
    keyboard_listener.stop()
    mouse_listener.stop()


if __name__ == "__main__":
    # Initalise the listeners
    keyboard_listener = keyboard.Listener(on_press=on_press)
    mouse_listener = mouse.Listener(on_click=on_click)
    keyboard_listener.start()
    mouse_listener.start()

    start_gui()
