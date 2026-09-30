import threading
import time
import keyboard
import mouse
from interfaces import IInputManager

class InputManager(IInputManager):
    def __init__(self):
        self.hotkey_name = "f8"
        self.is_binding = False
        self.is_catching_key = False
        
        self.on_toggle = None
        self.on_key_caught = None
        self.on_hotkey_bound = None

    def setup_listeners(self):
        keyboard.on_press(self._on_key_event)
        mouse.hook(self._on_mouse_event)

    def set_hotkey(self, key):
        self.hotkey_name = key

    def _on_key_event(self, event):
        if self.is_catching_key:
            self.is_catching_key = False
            if self.on_key_caught: self.on_key_caught(event.name)
            return

        if self.is_binding:
            self.is_binding = False
            if self.on_hotkey_bound: self.on_hotkey_bound(event.name)
            return

        if event.name == self.hotkey_name:
            if self.on_toggle: self.on_toggle()

    def _on_mouse_event(self, event):
        if isinstance(event, mouse.ButtonEvent) and event.event_type == 'down':
            if event.button == self.hotkey_name:
                if self.on_toggle: self.on_toggle()

    def start_key_catch(self):
        threading.Thread(target=self._catch_input_loop, daemon=True).start()
        
    def _catch_input_loop(self):
        try:
            while mouse.is_pressed('left'): time.sleep(0.01)
        except Exception: pass
        
        time.sleep(0.05)
        self.is_catching_key = True
        
        mouse_buttons = ['left', 'right', 'middle', 'x', 'x2']
        while self.is_catching_key:
            for btn in mouse_buttons:
                try:
                    if mouse.is_pressed(btn):
                        self.is_catching_key = False
                        if self.on_key_caught: self.on_key_caught(btn)
                        return
                except Exception: pass
            time.sleep(0.01)

    def start_binding(self):
        threading.Thread(target=self._bind_input_loop, daemon=True).start()

    def _bind_input_loop(self):
        try:
            while mouse.is_pressed('left'): time.sleep(0.01)
        except Exception: pass
        
        time.sleep(0.05)
        self.is_binding = True
        
        mouse_buttons = ['left', 'right', 'middle', 'x', 'x2']
        while self.is_binding:
            for btn in mouse_buttons:
                try:
                    if mouse.is_pressed(btn):
                        self.is_binding = False
                        if self.on_hotkey_bound: self.on_hotkey_bound(btn)
                        return
                except Exception: pass
            time.sleep(0.01)

    def wait_for_location_click(self, callback):
        threading.Thread(target=self._wait_location_click, args=(callback,), daemon=True).start()

    def _wait_location_click(self, callback):
        time.sleep(0.2) 
        while not mouse.is_pressed('left'):
            time.sleep(0.01)
        x, y = mouse.get_position()
        if callback: callback(x, y)