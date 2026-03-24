import ctypes
import os
import sys
import psutil
import keyboard
import time
import win32gui
import win32process
import win32con


def is_admin() -> bool:
    """Check if the application is running with administrator privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

def resource_path(relative_path) -> str:
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def _get_pid_by_name(process_name: str) -> int:
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == process_name:
            return proc.info['pid']
    return None

def _get_hwnd_for_pid(pid: int) -> int:
    def callback(hwnd, hwnds):
        _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
        if found_pid == pid:
            hwnds.append(hwnd)
    hwnds = []
    win32gui.EnumWindows(callback, hwnds)
    return hwnds[0] if hwnds else None

def _bring_window_to_front(hwnd: int) -> None:
    # restore window
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    # set window to foreground
    win32gui.SetForegroundWindow(hwnd)
    # # bring window to top
    # win32gui.BringWindowToTop(hwnd)
    # # set window to foreground again
    # win32gui.SetForegroundWindow(hwnd)

def jump_to_process_window(process_name: str) -> bool:
    pid = _get_pid_by_name(process_name)
    if pid is not None:
        hwnd = _get_hwnd_for_pid(pid)
        if hwnd is not None:
            _bring_window_to_front(hwnd)
            return True
    return False

def press_key(key_name: str) -> None:
    if str:
        keyboard.press(key_name)

def release_key(key_name: str) -> None:
    if str:
        keyboard.release(key_name)

def press_and_release_key(key_name: str, interval: float = 0.0) -> None:
    # print(f"Pressing key: {key_name} for {interval} seconds")
    # print(f"Current foreground window title: {win32gui.GetWindowText(win32gui.GetForegroundWindow())}")
    # keyboard.press(key_name)
    # if "shift" in key_name.lower():
    #     print("Shift key detected, adding minimum interval of 0.1 seconds")
    #     interval = min(interval, 0.5) # shift key must has some duration to be recognized by some games, otherwise it will be ignored
    #     time.sleep(interval)
    # keyboard.release(key_name)
    if str:
        keyboard.press_and_release(key_name)