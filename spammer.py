import threading
import time
import keyboard
import mouse # FARE KÜTÜPHANESİ EKLENDİ
import customtkinter as ctk
import json
import os

class SpammerBackend:
    def __init__(self, update_ui_callback):
        self.running = False
        self.keyboard_keys = []
        self.mouse_buttons = [] # FARE TUŞLARI İÇİN YENİ LİSTE
        self.delay = 0.1
        self.update_ui = update_ui_callback

    def set_params(self, keys_str, delay):
        self.keyboard_keys = []
        self.mouse_buttons = []
        
        # Girişi virgülle ayırıp temizle
        all_keys = [k.strip().lower() for k in keys_str.split(',') if k.strip()]
        
        # Klavyeyi mi fareyi mi kontrol edeceklerini ayrıştır
        for k in all_keys:
            if k in ['left', 'right', 'middle']:
                self.mouse_buttons.append(k)
            else:
                self.keyboard_keys.append(k)
                
        self.delay = delay

    def toggle(self):
        # Hiçbir tuş girilmemişse başlatma
        if not self.keyboard_keys and not self.mouse_buttons:
            return
        
        self.running = not self.running
        self.update_ui(self.running)
        
        if self.running:
            threading.Thread(target=self._spam_loop, daemon=True).start()

    def stop(self):
        self.running = False
        self.update_ui(self.running)

    def _spam_loop(self):
        while self.running:
            # KLAVYE tuşlarına bas
            for key in self.keyboard_keys:
                try:
                    keyboard.press(key)
                except Exception:
                    pass
                    
            # FARE tuşlarına bas
            for btn in self.mouse_buttons:
                try:
                    mouse.press(button=btn)
                except Exception:
                    pass
            
            time.sleep(0.005) 
            
            # KLAVYE tuşlarını bırak
            for key in self.keyboard_keys:
                try:
                    keyboard.release(key)
                except Exception:
                    pass
                    
            # FARE tuşlarını bırak
            for btn in self.mouse_buttons:
                try:
                    mouse.release(button=btn)
                except Exception:
                    pass
            
            time.sleep(max(0.01, self.delay))

class SpammerUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("MC AutoKey Spammer")
        self.geometry("350x550") # Fare ipucu için pencereyi biraz daha uzattık
        self.resizable(False, False)
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.backend = SpammerBackend(self.update_status)
        
        self.hotkey_name = "f8"
        self.is_binding = False
        
        self.profiles_file = "profiles.json"
        self.profiles = self.load_profiles_from_file()

        self.setup_ui()
        self.setup_global_listener()
        self.load_initial_profile()

    def load_profiles_from_file(self):
        if os.path.exists(self.profiles_file):
            try:
                with open(self.profiles_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def save_profiles_to_file(self):
        with open(self.profiles_file, "w", encoding="utf-8") as f:
            json.dump(self.profiles, f, indent=4, ensure_ascii=False)

    def setup_ui(self):
        # 1. BÖLÜM: Profil Yönetimi
        self.frame_profile = ctk.CTkFrame(self)
        self.frame_profile.pack(pady=(15, 5), padx=20, fill="x")

        self.lbl_profile = ctk.CTkLabel(self.frame_profile, text="Profil Seç / Yeni İsim Yaz:", font=("Arial", 12))
        self.lbl_profile.pack(pady=(10, 0))

        profile_names = list(self.profiles.keys()) if self.profiles else ["Varsayılan"]
        self.cmb_profile = ctk.CTkComboBox(self.frame_profile, values=profile_names, command=self.on_profile_selected)
        self.cmb_profile.pack(pady=5, padx=10, fill="x")

        self.btn_save_profile = ctk.CTkButton(self.frame_profile, text="Geçerli Ayarları Kaydet", command=self.save_current_profile)
        self.btn_save_profile.pack(pady=(0, 10), padx=10, fill="x")

        # 2. BÖLÜM: Kısayol Ayarı
        self.frame_hotkey = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_hotkey.pack(pady=5, padx=20, fill="x")
        
        self.lbl_hotkey = ctk.CTkLabel(self.frame_hotkey, text=f"Kısayol: {self.hotkey_name.upper()}", font=("Arial", 14, "bold"))
        self.lbl_hotkey.pack(side="left", padx=5)
        
        self.btn_bind = ctk.CTkButton(self.frame_hotkey, text="Tuşu Değiştir", width=100, fg_color="#3498DB", hover_color="#2980B9", command=self.start_binding)
        self.btn_bind.pack(side="right", padx=5)

        # 3. BÖLÜM: Tuş ve Gecikme Ayarları
        # Fare tuşları için ipucu eklendi
        self.lbl_keys = ctk.CTkLabel(self, text="Tuşlar (w, space, left, right):", font=("Arial", 12))
        self.lbl_keys.pack(pady=(10, 0))
        
        self.ent_keys = ctk.CTkEntry(self, width=250, placeholder_text="w, left")
        self.ent_keys.pack(pady=5)

        self.lbl_delay = ctk.CTkLabel(self, text="Gecikme (Saniye):", font=("Arial", 12))
        self.lbl_delay.pack(pady=(5, 0))
        
        self.ent_delay = ctk.CTkEntry(self, width=250, placeholder_text="0.1")
        self.ent_delay.insert(0, "0.1")
        self.ent_delay.pack(pady=5)

        self.btn_apply = ctk.CTkButton(self, text="Ayarları Uygula", command=self.apply_settings, fg_color="#E67E22", hover_color="#D35400")
        self.btn_apply.pack(pady=15)

        # 4. BÖLÜM: Durum
        self.lbl_status = ctk.CTkLabel(self, text="DURUYOR", text_color="#ff4c4c", font=("Arial", 16, "bold"))
        self.lbl_status.pack(pady=5)

    def setup_global_listener(self):
        keyboard.on_press(self._on_key_event)

    def _on_key_event(self, event):
        if self.is_binding:
            self.is_binding = False
            new_key = event.name
            self.after(0, self.update_hotkey, new_key)
            self.after(0, lambda: self.btn_bind.configure(text="Tuşu Değiştir", state="normal"))
            return

        if event.name == self.hotkey_name:
            self.backend.toggle()

    def update_hotkey(self, new_key):
        if self.backend.running:
            self.backend.stop()
                
        self.hotkey_name = new_key
        self.lbl_hotkey.configure(text=f"Kısayol: {self.hotkey_name.upper()}")
        self.update_status(False)

    def start_binding(self):
        if self.backend.running:
            self.backend.stop()
            
        self.is_binding = True
        self.btn_bind.configure(text="Basın...", state="disabled")
        self.lbl_status.configure(text="YENİ TUŞ BEKLENİYOR", text_color="#f39c12")

    def load_initial_profile(self):
        if self.profiles:
            first_profile = list(self.profiles.keys())[0]
            self.cmb_profile.set(first_profile)
            self.on_profile_selected(first_profile)

    def on_profile_selected(self, choice):
        if choice in self.profiles:
            data = self.profiles[choice]
            
            self.ent_keys.delete(0, 'end')
            self.ent_keys.insert(0, data.get("keys", ""))
            
            self.ent_delay.delete(0, 'end')
            self.ent_delay.insert(0, str(data.get("delay", "0.1")))
            
            new_hotkey = data.get("hotkey", "f8")
            self.update_hotkey(new_hotkey)
            
            self.apply_settings()

    def save_current_profile(self):
        profile_name = self.cmb_profile.get().strip()
        if not profile_name:
            return
            
        self.profiles[profile_name] = {
            "keys": self.ent_keys.get(),
            "delay": self.ent_delay.get(),
            "hotkey": self.hotkey_name
        }
        self.save_profiles_to_file()
        
        self.cmb_profile.configure(values=list(self.profiles.keys()))
        self.apply_settings()

    def apply_settings(self):
        keys = self.ent_keys.get()
        try:
            delay = float(self.ent_delay.get())
        except ValueError:
            delay = 0.1
        self.backend.set_params(keys, delay)

    def update_status(self, is_running):
        if is_running:
            self.lbl_status.configure(text=f"ÇALIŞIYOR ({self.hotkey_name.upper()})", text_color="#2ecc71")
        else:
            self.lbl_status.configure(text=f"DURUYOR ({self.hotkey_name.upper()})", text_color="#ff4c4c")

if __name__ == "__main__":
    app = SpammerUI()
    app.mainloop()