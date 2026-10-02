import threading
import time
from pynput.keyboard import Controller as KbdController, Key
from pynput.mouse import Controller as MouseController, Button
from interfaces import IEngine

class KeyboardEngine(IEngine):
    def __init__(self, on_status_change):
        self.running = False
        self.key = ""
        self.delay = 0.1
        self.on_status_change = on_status_change
        self.keyboard = KbdController()
        
        # Pynput özel tuşları için eşleştirme
        self.special_keys = {
            'space': Key.space, 'enter': Key.enter, 'shift': Key.shift,
            'ctrl': Key.ctrl, 'alt': Key.alt, 'tab': Key.tab, 'esc': Key.esc
        }

    def set_params(self, key_str, delay):
        key_str = key_str.strip().lower()
        # Eğer özel tuşsa pynput nesnesini al, değilse string olarak bırak
        self.key = self.special_keys.get(key_str, key_str)
        self.delay = delay

    def toggle(self):
        if not self.key: return
        self.running = not self.running
        self.on_status_change(self.running)
        if self.running:
            threading.Thread(target=self._spam_loop, daemon=True).start()

    def stop(self):
        self.running = False
        self.on_status_change(self.running)

    def _spam_loop(self):
        while self.running:
            try:
                self.keyboard.press(self.key)
                time.sleep(0.005)
                self.keyboard.release(self.key)
            except Exception:
                pass
            time.sleep(max(0.01, self.delay))

class MouseEngine(IEngine):
    def __init__(self, on_status_change):
        self.running = False
        self.on_status_change = on_status_change
        self.mouse = MouseController()
        
        self.interval = 0.1
        self.button = Button.left
        self.click_type = "Single"
        self.repeat_mode = "until_stopped"
        self.repeat_times = 1
        self.pos_mode = "current"
        self.pos_x = 0
        self.pos_y = 0

    def set_params(self, interval, button_str, click_type, repeat_mode, repeat_times, pos_mode, pos_x, pos_y):
        self.interval = max(0.01, interval)
        
        btn_map = {"Sol Tık": Button.left, "Sağ Tık": Button.right, "Orta Tık": Button.middle}
        self.button = btn_map.get(button_str, Button.left)
        
        self.click_type = click_type
        self.repeat_mode = repeat_mode
        self.repeat_times = repeat_times
        self.pos_mode = pos_mode
        self.pos_x = pos_x
        self.pos_y = pos_y

    def toggle(self):
        self.running = not self.running
        self.on_status_change(self.running)
        if self.running:
            threading.Thread(target=self._spam_loop, daemon=True).start()

    def stop(self):
        self.running = False
        self.on_status_change(self.running)

    def _spam_loop(self):
        count = 0
        while self.running:
            if self.pos_mode == "picked":
                self.mouse.position = (self.pos_x, self.pos_y)

            try:
                click_count = 2 if self.click_type == "Double" else 1
                self.mouse.click(self.button, click_count)
            except Exception:
                pass

            if self.repeat_mode == "times":
                count += 1
                if count >= self.repeat_times:
                    self.stop()
                    break

            time.sleep(self.interval)