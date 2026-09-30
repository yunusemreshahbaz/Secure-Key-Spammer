import threading
import time
import keyboard
import mouse
from interfaces import IEngine

class KeyboardEngine(IEngine):
    def __init__(self, on_status_change):
        self.running = False
        self.key = ""
        self.delay = 0.1
        self.on_status_change = on_status_change

    def set_params(self, key_str, delay):
        self.key = key_str.strip().lower()
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
                if not keyboard.is_pressed(self.key):
                    keyboard.press(self.key)
                    time.sleep(0.005)
                    keyboard.release(self.key)
            except Exception:
                pass
            time.sleep(max(0.01, self.delay))

class MouseEngine(IEngine):
    def __init__(self, on_status_change):
        self.running = False
        self.on_status_change = on_status_change
        
        self.interval = 0.1
        self.button = "left"
        self.click_type = "Single"
        self.repeat_mode = "until_stopped"
        self.repeat_times = 1
        self.pos_mode = "current"
        self.pos_x = 0
        self.pos_y = 0

    def set_params(self, interval, button, click_type, repeat_mode, repeat_times, pos_mode, pos_x, pos_y):
        self.interval = max(0.01, interval)
        btn_map = {"Sol Tık": "left", "Sağ Tık": "right", "Orta Tık": "middle"}
        self.button = btn_map.get(button, "left")
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
                mouse.move(self.pos_x, self.pos_y)

            try:
                if self.click_type == "Double":
                    mouse.double_click(button=self.button)
                else:
                    mouse.click(button=self.button)
            except Exception:
                pass

            if self.repeat_mode == "times":
                count += 1
                if count >= self.repeat_times:
                    self.stop()
                    break

            time.sleep(self.interval)