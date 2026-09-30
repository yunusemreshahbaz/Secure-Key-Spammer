import threading
import time
import keyboard
import customtkinter as ctk

class SpammerBackend:
    def __init__(self, update_ui_callback):
        self.running = False
        self.keys = []
        self.delay = 0.1
        self.update_ui = update_ui_callback

    def set_params(self, keys_str, delay):
        # Virgülle ayrılmış tuşları temizleyip listeye çevirir
        self.keys = [k.strip().lower() for k in keys_str.split(',') if k.strip()]
        self.delay = delay

    def toggle(self):
        if not self.keys:
            return
        
        self.running = not self.running
        self.update_ui(self.running) # Arayüzdeki metni günceller
        
        if self.running:
            # Arayüzü dondurmamak için spam işlemini ayrı bir thread'de başlatır
            threading.Thread(target=self._spam_loop, daemon=True).start()

    def _spam_loop(self):
        while self.running:
            # Tüm tuşlara aynı anda bas
            for key in self.keys:
                keyboard.press(key)
            
            # Tüm tuşları aynı anda bırak
            for key in self.keys:
                keyboard.release(key)
            
            time.sleep(self.delay)

class SpammerUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("MC AutoKey Spammer")
        self.geometry("350x300")
        self.resizable(False, False)
        
        # Modern UI teması
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.backend = SpammerBackend(self.update_status)
        
        # Global kısayol ataması (Uygulama arka plandayken bile F8 ile çalışır)
        self.hotkey = "f8"
        keyboard.add_hotkey(self.hotkey, self.backend.toggle)

        self.setup_ui()

    def setup_ui(self):
        self.lbl_keys = ctk.CTkLabel(self, text="Spamlanacak Tuşlar (Örn: w, space, q):", font=("Arial", 14))
        self.lbl_keys.pack(pady=(20, 5))
        
        self.ent_keys = ctk.CTkEntry(self, width=250, placeholder_text="w, space")
        self.ent_keys.pack()

        self.lbl_delay = ctk.CTkLabel(self, text="Gecikme (Saniye):", font=("Arial", 14))
        self.lbl_delay.pack(pady=(15, 5))
        
        self.ent_delay = ctk.CTkEntry(self, width=250, placeholder_text="0.1")
        self.ent_delay.insert(0, "0.1")
        self.ent_delay.pack()

        self.btn_save = ctk.CTkButton(self, text="Ayarları Uygula", command=self.apply_settings)
        self.btn_save.pack(pady=20)

        self.lbl_status = ctk.CTkLabel(self, text=f"DURUYOR (Başlatmak için {self.hotkey.upper()})", 
                                       text_color="#ff4c4c", font=("Arial", 16, "bold"))
        self.lbl_status.pack(pady=10)

    def apply_settings(self):
        keys = self.ent_keys.get()
        try:
            delay = float(self.ent_delay.get())
        except ValueError:
            delay = 0.1 # Hatalı girişte varsayılan değer
        self.backend.set_params(keys, delay)

    def update_status(self, is_running):
        if is_running:
            self.lbl_status.configure(text=f"ÇALIŞIYOR (Durdurmak için {self.hotkey.upper()})", text_color="#2ecc71")
        else:
            self.lbl_status.configure(text=f"DURUYOR (Başlatmak için {self.hotkey.upper()})", text_color="#ff4c4c")

if __name__ == "__main__":
    app = SpammerUI()
    app.mainloop()