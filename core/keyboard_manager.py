import keyboard
import time
import win32con
import win32gui
import win32api
from utils.system_utils import get_process_hwnd, send_activate_message
from models import KeyOutConfig

from logger import get_logger

class KeyboardManager:
    min_activate_interval = 50 # milliseconds
    key_name_map = {
        "left ctrl": win32con.VK_LCONTROL,
        "left shift": win32con.VK_LSHIFT,
        "space": win32con.VK_SPACE,
        "f1": win32con.VK_F1,
        "f2": win32con.VK_F2,
        "f3": win32con.VK_F3,
        "f4": win32con.VK_F4,
        "f5": win32con.VK_F5,
        "f6": win32con.VK_F6,
        "f7": win32con.VK_F7,
        "f8": win32con.VK_F8,
        "f9": win32con.VK_F9,
        "f10": win32con.VK_F10,
        "f11": win32con.VK_F11,
        "f12": win32con.VK_F12,
    }

    def __init__(self, key_out_config: KeyOutConfig):
        self._config = key_out_config
        self._hwnd = get_process_hwnd(key_out_config.target_process)
        self._last_activated_time = 0
        self._logger = get_logger(__name__)

    def press_key(self, key_name: str):
        if not key_name:
            return
        if self._config.background_input:
            if not self._hwnd:
                self._hwnd = get_process_hwnd(self._config.target_process)
                if not self._hwnd:
                    self._logger.warning(f"Cannot find window for process '{self._config.target_process}', failed to send background key input '{key_name}'")
                    return
            vk_code = self._key_name_to_vk_code(key_name)
            self._ensure_activated()
            win32gui.PostMessage(self._hwnd, win32con.WM_KEYDOWN, vk_code, self._make_lparam(vk_code, True))
        else:
            keyboard.press(key_name)

    def release_key(self, key_name: str):
        if not key_name:
            return
        if self._config.background_input:
            if not self._hwnd:
                self._hwnd = get_process_hwnd(self._config.target_process)
                if not self._hwnd:
                    self._logger.warning(f"Cannot find window for process '{self._config.target_process}', failed to send background key input '{key_name}'")
                    return
            vk_code = self._key_name_to_vk_code(key_name)
            self._ensure_activated()
            win32gui.PostMessage(self._hwnd, win32con.WM_KEYUP, vk_code, self._make_lparam(vk_code, False))
        else:
            keyboard.release(key_name)

    def press_and_release_key(self, key_name: str):
        if not key_name:
            return
        if self._config.background_input:
            if not self._hwnd:
                self._hwnd = get_process_hwnd(self._config.target_process)
                if not self._hwnd:
                    self._logger.warning(f"Cannot find window for process '{self._config.target_process}', failed to send background key input '{key_name}'")
                    return
            vk_code = self._key_name_to_vk_code(key_name)
            self._ensure_activated()
            win32gui.PostMessage(self._hwnd, win32con.WM_KEYDOWN, vk_code, self._make_lparam(vk_code, True))
            win32gui.PostMessage(self._hwnd, win32con.WM_KEYUP, vk_code, self._make_lparam(vk_code, False))
        else:
            keyboard.press_and_release(key_name)
    
    def _ensure_activated(self):
        if self._hwnd:
            current_time = time.time() * 1000
            if current_time - self._last_activated_time > self.min_activate_interval:
                send_activate_message(self._hwnd)
                self._last_activated_time = current_time
    
    @classmethod
    def _key_name_to_vk_code(cls, key_name: str) -> int:
        # check if key_name is a single character and can be converted to VK code
        if len(key_name) == 1:
            vk_code = win32api.VkKeyScan(key_name)
            if vk_code != -1:
                return vk_code & 0xFF
            else:
                raise ValueError(f"Cannot convert key name '{key_name}' to VK code")
        else:
            if key_name in cls.key_name_map:
                return cls.key_name_map[key_name]
            else:
                raise ValueError(f"Key name '{key_name}' not found in key name map")
    
    @staticmethod
    def _make_lparam(vk_code: int, is_key_down: bool) -> int:
        scan_code = win32api.MapVirtualKey(vk_code, 0)
        lparam = 1
        lparam |= (scan_code << 16)
        if not is_key_down:
            lparam |= (1 << 31)
        return lparam
