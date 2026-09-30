import threading
import time
import keyboard
import customtkinter as ctk
import json
import os

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
        self.geometry("350x450") # Yeni araçlar için pencereyi biraz uzattık
        self.resizable(False, False)

        # Modern UI teması
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.backend = SpammerBackend(self.update_status)

        # Global kısayol ataması (Uygulama arka plandayken bile F8 ile çalışır)
        self.hotkey = "f8"
        keyboard.add_hotkey(self.hotkey, self.backend.toggle)

        # Profil Sistemi Başlatma
        self.profiles_file = "profiles.json"
        self.profiles = self.load_profiles_from_file()

        self.setup_ui()
        self.load_initial_profile()

    def load_profiles_from_file(self):
        """JSON dosyasını okur, yoksa boş bir sözlük döndürür."""
        if os.path.exists(self.profiles_file):
            try:
                with open(self.profiles_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Profil okuma hatası: {e}")
        return {}

    def save_profiles_to_file(self):
        """Sözlükteki verileri JSON dosyasına kaydeder."""
        with open(self.profiles_file, "w", encoding="utf-8") as f:
            json.dump(self.profiles, f, indent=4, ensure_ascii=False)

    def setup_ui(self):
        # 1. BÖLÜM: Profil Yönetimi
        self.frame_profile = ctk.CTkFrame(self)
        self.frame_profile.pack(pady=15, padx=20, fill="x")

        self.lbl_profile = ctk.CTkLabel(self.frame_profile, text="Profil Seç / Yeni İsim Yaz:", font=("Arial", 12))
        self.lbl_profile.pack(pady=(10, 0))

        # ComboBox hem seçim yapmayı hem de yeni metin girmeyi sağlar
        profile_names = list(self.profiles.keys()) if self.profiles else ["Varsayılan"]
        self.cmb_profile = ctk.CTkComboBox(self.frame_profile, values=profile_names, command=self.on_profile_selected)
        self.cmb_profile.pack(pady=5, padx=10, fill="x")

        self.btn_save_profile = ctk.CTkButton(self.frame_profile, text="Geçerli Ayarları Kaydet", command=self.save_current_profile)
        self.btn_save_profile.pack(pady=(0, 10), padx=10, fill="x")

        # 2. BÖLÜM: Tuş ve Gecikme Ayarları
        self.lbl_keys = ctk.CTkLabel(self, text="Spamlanacak Tuşlar (Örn: w, space):", font=("Arial", 14))
        self.lbl_keys.pack(pady=(10, 5))
        
        self.ent_keys = ctk.CTkEntry(self, width=250, placeholder_text="w, space")
        self.ent_keys.pack()

        self.lbl_delay = ctk.CTkLabel(self, text="Gecikme (Saniye):", font=("Arial", 14))
        self.lbl_delay.pack(pady=(10, 5))
        
        self.ent_delay = ctk.CTkEntry(self, width=250, placeholder_text="0.1")
        self.ent_delay.insert(0, "0.1")
        self.ent_delay.pack()

        self.btn_apply = ctk.CTkButton(self, text="Ayarları Uygula", command=self.apply_settings, fg_color="#E67E22", hover_color="#D35400")
        self.btn_apply.pack(pady=20)

        # 3. BÖLÜM: Durum
        self.lbl_status = ctk.CTkLabel(self, text=f"DURUYOR ({self.hotkey.upper()})", 
                                       text_color="#ff4c4c", font=("Arial", 16, "bold"))
        self.lbl_status.pack(pady=5)

    def load_initial_profile(self):
        """Uygulama açıldığında ilk profili yükler."""
        if self.profiles:
            first_profile = list(self.profiles.keys())[0]
            self.cmb_profile.set(first_profile)
            self.on_profile_selected(first_profile)

    def on_profile_selected(self, choice):
        """Açılır menüden bir profil seçildiğinde kutuları doldurur."""
        if choice in self.profiles:
            data = self.profiles[choice]
            
            self.ent_keys.delete(0, 'end')
            self.ent_keys.insert(0, data.get("keys", ""))
            
            self.ent_delay.delete(0, 'end')
            self.ent_delay.insert(0, str(data.get("delay", "0.1")))
            
            self.apply_settings() # Seçilir seçilmez backend'e gönder

    def save_current_profile(self):
        """Kutulardaki mevcut ayarları girilen isimle JSON'a kaydeder."""
        profile_name = self.cmb_profile.get().strip()
        if not profile_name:
            return
            
        self.profiles[profile_name] = {
            "keys": self.ent_keys.get(),
            "delay": self.ent_delay.get()
        }
        self.save_profiles_to_file()
        
        # ComboBox listesini güncelle
        self.cmb_profile.configure(values=list(self.profiles.keys()))
        self.apply_settings()

    def apply_settings(self):
        """UI'daki değerleri backend motoruna iletir."""
        keys = self.ent_keys.get()
        try:
            delay = float(self.ent_delay.get())
        except ValueError:
            delay = 0.1 # Hatalı girişte varsayılan değer
        self.backend.set_params(keys, delay)

    def update_status(self, is_running):
        if is_running:
            self.lbl_status.configure(text=f"ÇALIŞIYOR ({self.hotkey.upper()})", text_color="#2ecc71")
        else:
            self.lbl_status.configure(text=f"DURUYOR ({self.hotkey.upper()})", text_color="#ff4c4c")

if __name__ == "__main__":
    app = SpammerUI()
    app.mainloop()