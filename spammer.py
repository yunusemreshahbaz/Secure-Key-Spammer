from ui import SpammerUI
from engines import KeyboardEngine, MouseEngine
from profile_manager import ProfileManager
from input_manager import InputManager

if __name__ == "__main__":
    # 1. Somut sınıfların oluşturulması
    profile_manager = ProfileManager()
    input_manager = InputManager()
    
    # UI metotları engine'lere veriliyor (Callback)
    # Status değiştiğinde ui'a bildirebilmeleri için.
    def ui_status_update(is_running):
        app.update_status(is_running)

    kbd_engine = KeyboardEngine(ui_status_update)
    mouse_engine = MouseEngine(ui_status_update)

    # 2. Bağımlılıkların UI'a enjekte edilmesi
    app = SpammerUI(kbd_engine, mouse_engine, profile_manager, input_manager)
    
    # 3. Uygulamanın başlatılması
    app.mainloop()