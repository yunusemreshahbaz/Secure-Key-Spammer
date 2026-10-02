from pynput import keyboard, mouse
from interfaces import IInputManager
import time

class InputManager(IInputManager):
    def __init__(self):
        self.hotkey_name = "f8"
        self.is_binding = False
        self.is_catching_key = False
        
        self.on_toggle = None
        self.on_key_caught = None
        self.on_hotkey_bound = None
        
        self.mouse_controller = mouse.Controller()
        
        self.kbd_listener = None
        self.mouse_listener = None
        
        # Olay bayrakları (Thread kilitlenmelerini önlemek için)
        self._picking_location = False
        self._location_callback = None

    def setup_listeners(self):
        # Listener'ları başlat
        self.kbd_listener = keyboard.Listener(on_press=self._on_key_press)
        self.kbd_listener.start()
        
        self.mouse_listener = mouse.Listener(on_click=self._on_mouse_click)
        self.mouse_listener.start()

    def set_hotkey(self, key):
        self.hotkey_name = str(key).replace("'", "") # 'w' formatını düzeltir

    def _format_key(self, key):
        """Pynput'un karmaşık tuş objelerini temiz stringlere dönüştürür."""
        try:
            # Harf tuşları için (char)
            return key.char.lower()
        except AttributeError:
            # Özel tuşlar için (Key.space, Key.f8 vb.)
            return key.name.lower()

    def _format_mouse_btn(self, button):
        """Pynput fare objesini stringe dönüştürür."""
        return button.name.lower() # left, right, middle

    def _on_key_press(self, key):
        if key is None: return
        key_str = self._format_key(key)

        if self.is_catching_key:
            self.is_catching_key = False
            if self.on_key_caught: self.on_key_caught(key_str)
            return

        if self.is_binding:
            self.is_binding = False
            if self.on_hotkey_bound: self.on_hotkey_bound(key_str)
            return

        if key_str == self.hotkey_name:
            if self.on_toggle: self.on_toggle()

    def _on_mouse_click(self, x, y, button, pressed):
        if not pressed: return # Sadece tuşa basıldığında (aşağı inerken) tepki ver
        
        btn_str = self._format_mouse_btn(button)

        # Konum seçme modu
        if self._picking_location and btn_str == 'left':
            self._picking_location = False
            if self._location_callback: self._location_callback(int(x), int(y))
            return

        # Klavye tuşu seçerken yanlışlıkla fareye basmayı engelle (sadece klavye istiyoruz)
        # Eğer özel olarak istenirse buraya fare tuşu ekleme mantığı eklenebilir.
        if self.is_catching_key:
            return 
            
        if self.is_binding:
            self.is_binding = False
            if self.on_hotkey_bound: self.on_hotkey_bound(btn_str)
            return

        if btn_str == self.hotkey_name:
            if self.on_toggle: self.on_toggle()

    def start_key_catch(self):
        # Biraz bekle ki butona tıkladığımız an algılanmasın
        time.sleep(0.1)
        self.is_catching_key = True

    def start_binding(self):
        time.sleep(0.1)
        self.is_binding = True

    def wait_for_location_click(self, callback):
        time.sleep(0.1)
        self._location_callback = callback
        self._picking_location = True