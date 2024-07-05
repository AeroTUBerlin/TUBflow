from screeninfo import get_monitors
import tkinter as tk

def target_monitor_resolution():
    root = tk.Tk()

    # Get the current window's position
    window_x = root.winfo_x()
    window_y = root.winfo_y()

    monitors = get_monitors()
    target_monitor = None

    # Find the monitor that contains the window
    for monitor in monitors:
        if (
            monitor.x <= window_x <= monitor.x + monitor.width and
            monitor.y <= window_y <= monitor.y + monitor.height
        ):
            target_monitor = monitor
            break

    if target_monitor:
        screen_width = target_monitor.width
        screen_height = target_monitor.height
    else:
        print("Monitor not found.")

    root.destroy()
    screen_dimensions = (screen_width, screen_height)

    return target_monitor, screen_dimensions