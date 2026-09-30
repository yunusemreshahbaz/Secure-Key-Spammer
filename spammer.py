import threading
import time
import keyboard
import mouse
import customtkinter as ctk
import json
import os

# ==========================================
# 1. KLAVYE MOTORU
# ==========================================
class KeyboardBackend:
    def __init__(self, update_ui_callback):
        self.running = False
        self.key = ""
        self.delay = 0.1
        self.update_ui = update_ui_callback

    def set_params(self, key_str, delay):
        self.key = key_str.strip().lower()
        self.delay = delay

    def toggle(self):
        if not self.key:
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
            try:
                # Fiziksel olarak tuşa basılı tutulmuyorsa spamla (kesintiyi önler)
                if not keyboard.is_pressed(self.key):
                    keyboard.press(self.key)
                    time.sleep(0.005)
                    keyboard.release(self.key)
            except Exception:
                pass
            time.sleep(max(0.01, self.delay))

# ==========================================
# 2. FARE MOTORU (OP Auto Clicker Mantığı)
# ==========================================
class MouseBackend:
    def __init__(self, update_ui_callback):
        self.running = False
        self.update_ui = update_ui_callback
        
        # Varsayılan ayarlar
        self.interval = 0.1
        self.button = "left"
        self.click_type = "Single"
        self.repeat_mode = "until_stopped"
        self.repeat_times = 1
        self.pos_mode = "current"
        self.pos_x = 0
        self.pos_y = 0

    def set_params(self, interval, button, click_type, repeat_mode, repeat_times, pos_mode, pos_x, pos_y):
        self.interval = max(0.01, interval) # Minimum 10ms güvenlik sınırı
        
        # İngilizce karşılıklarına çevir
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
        self.update_ui(self.running)
        
        if self.running:
            threading.Thread(target=self._spam_loop, daemon=True).start()

    def stop(self):
        self.running = False
        self.update_ui(self.running)

    def _spam_loop(self):
        count = 0
        while self.running:
            # İstenen konuma git
            if self.pos_mode == "picked":
                mouse.move(self.pos_x, self.pos_y)

            # Tıklama işlemi
            try:
                if self.click_type == "Double":
                    mouse.double_click(button=self.button)
                else:
                    mouse.click(button=self.button)
            except Exception:
                pass

            # Tekrar sayısı kontrolü
            if self.repeat_mode == "times":
                count += 1
                if count >= self.repeat_times:
                    self.stop()
                    break

            time.sleep(self.interval)

# ==========================================
# 3. ARAYÜZ (UI)
# ==========================================
class SpammerUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("MC AutoKey & Clicker")
        self.geometry("520x650")
        self.resizable(False, False)
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Motorlar
        self.kbd_backend = KeyboardBackend(self.update_status)
        self.mouse_backend = MouseBackend(self.update_status)
        
        self.hotkey_name = "f8"
        self.is_binding = False
        self.is_catching_key = False
        
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
        # ÜST KISIM: SEKMELER (TABS)
        self.tabview = ctk.CTkTabview(self, width=480, height=480)
        self.tabview.pack(pady=(10, 5), padx=20, fill="both", expand=True)
        
        self.tab_kbd = self.tabview.add("Klavye")
        self.tab_mouse = self.tabview.add("Fare")

        self.setup_keyboard_tab()
        self.setup_mouse_tab()

        # ALT KISIM: ORTAK KISAYOL VE DURUM EKRANI
        self.frame_bottom = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_bottom.pack(pady=5, padx=20, fill="x")
        
        self.lbl_status = ctk.CTkLabel(self.frame_bottom, text="DURUYOR", text_color="#ff4c4c", font=("Arial", 18, "bold"))
        self.lbl_status.pack(pady=5)
        
        self.frame_hotkey = ctk.CTkFrame(self.frame_bottom, fg_color="#2b2b2b", corner_radius=10)
        self.frame_hotkey.pack(pady=5, fill="x", ipadx=10, ipady=10)
        
        self.lbl_hotkey = ctk.CTkLabel(self.frame_hotkey, text=f"Kısayol: {self.hotkey_name.upper()}", font=("Arial", 14, "bold"))
        self.lbl_hotkey.pack(side="left", padx=15)
        
        self.btn_bind = ctk.CTkButton(self.frame_hotkey, text="Tuşu Değiştir", width=120, fg_color="#3498DB", hover_color="#2980B9", command=self.start_binding)
        self.btn_bind.pack(side="right", padx=15)

    def setup_keyboard_tab(self):
        # 1. Profil Yönetimi
        frame_profile = ctk.CTkFrame(self.tab_kbd)
        frame_profile.pack(pady=(10, 15), padx=10, fill="x")

        ctk.CTkLabel(frame_profile, text="Profil Seç / Yeni İsim Yaz:", font=("Arial", 12)).pack(pady=(10, 0))
        
        profile_names = list(self.profiles.keys()) if self.profiles else ["Varsayılan"]
        self.cmb_profile = ctk.CTkComboBox(frame_profile, values=profile_names, command=self.on_profile_selected)
        self.cmb_profile.pack(pady=5, padx=10, fill="x")

        ctk.CTkButton(frame_profile, text="Ayarları Kaydet", command=self.save_current_profile).pack(pady=(0, 10), padx=10, fill="x")

        # 2. Klavye Tuş Seçimi
        ctk.CTkLabel(self.tab_kbd, text="Spamlanacak Tuş:", font=("Arial", 12, "bold")).pack(pady=(10, 0))
        
        frame_keys = ctk.CTkFrame(self.tab_kbd, fg_color="transparent")
        frame_keys.pack(pady=5)
        
        self.ent_keys = ctk.CTkEntry(frame_keys, width=150, placeholder_text="Örn: w, space, 1", justify="center")
        self.ent_keys.pack(side="left", padx=5)
        
        self.btn_add_key = ctk.CTkButton(frame_keys, text="Seç", width=60, fg_color="#2ECC71", hover_color="#27AE60", command=self.start_key_catch)
        self.btn_add_key.pack(side="left")

        # 3. Gecikme
        ctk.CTkLabel(self.tab_kbd, text="Gecikme (Saniye):", font=("Arial", 12, "bold")).pack(pady=(15, 0))
        self.ent_delay = ctk.CTkEntry(self.tab_kbd, width=150, justify="center")
        self.ent_delay.insert(0, "0.1")
        self.ent_delay.pack(pady=5)

        self.btn_apply_kbd = ctk.CTkButton(self.tab_kbd, text="Ayarları Uygula", command=self.apply_kbd_settings, fg_color="#E67E22", hover_color="#D35400")
        self.btn_apply_kbd.pack(pady=20)

    def setup_mouse_tab(self):
        # 1. Tıklama Aralığı (Click Interval)
        frame_interval = ctk.CTkFrame(self.tab_mouse)
        frame_interval.pack(pady=10, padx=10, fill="x")
        ctk.CTkLabel(frame_interval, text="Tıklama Aralığı", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=5)
        
        row_interval = ctk.CTkFrame(frame_interval, fg_color="transparent")
        row_interval.pack(pady=5, padx=10, fill="x")
        
        self.ent_h = ctk.CTkEntry(row_interval, width=40, justify="center")
        self.ent_h.insert(0, "0")
        self.ent_h.pack(side="left", padx=(0,5))
        ctk.CTkLabel(row_interval, text="saat").pack(side="left", padx=(0,10))
        
        self.ent_m = ctk.CTkEntry(row_interval, width=40, justify="center")
        self.ent_m.insert(0, "0")
        self.ent_m.pack(side="left", padx=(0,5))
        ctk.CTkLabel(row_interval, text="dk").pack(side="left", padx=(0,10))
        
        self.ent_s = ctk.CTkEntry(row_interval, width=40, justify="center")
        self.ent_s.insert(0, "0")
        self.ent_s.pack(side="left", padx=(0,5))
        ctk.CTkLabel(row_interval, text="sn").pack(side="left", padx=(0,10))
        
        self.ent_ms = ctk.CTkEntry(row_interval, width=60, justify="center")
        self.ent_ms.insert(0, "100")
        self.ent_ms.pack(side="left", padx=(0,5))
        ctk.CTkLabel(row_interval, text="ms").pack(side="left")

        # Orta Bölüm (Seçenekler ve Tekrar)
        frame_middle = ctk.CTkFrame(self.tab_mouse, fg_color="transparent")
        frame_middle.pack(pady=5, padx=10, fill="x")

        # 2. Tıklama Seçenekleri (Click Options)
        frame_opts = ctk.CTkFrame(frame_middle, width=200)
        frame_opts.pack(side="left", fill="both", expand=True, padx=(0, 5))
        ctk.CTkLabel(frame_opts, text="Tıklama Seçenekleri", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=5)
        
        opt1 = ctk.CTkFrame(frame_opts, fg_color="transparent")
        opt1.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(opt1, text="Tuş:").pack(side="left")
        self.cmb_btn = ctk.CTkOptionMenu(opt1, values=["Sol Tık", "Sağ Tık", "Orta Tık"], width=100)
        self.cmb_btn.pack(side="right")
        
        opt2 = ctk.CTkFrame(frame_opts, fg_color="transparent")
        opt2.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(opt2, text="Tip:").pack(side="left")
        self.cmb_type = ctk.CTkOptionMenu(opt2, values=["Single", "Double"], width=100)
        self.cmb_type.pack(side="right")

        # 3. Tıklama Tekrarı (Click Repeat)
        frame_repeat = ctk.CTkFrame(frame_middle, width=200)
        frame_repeat.pack(side="right", fill="both", expand=True, padx=(5, 0))
        ctk.CTkLabel(frame_repeat, text="Tekrar Modu", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=5)
        
        self.repeat_var = ctk.StringVar(value="until_stopped")
        
        rep1 = ctk.CTkFrame(frame_repeat, fg_color="transparent")
        rep1.pack(fill="x", padx=10, pady=5)
        self.rad_times = ctk.CTkRadioButton(rep1, text="Şu kadar tekrarla:", variable=self.repeat_var, value="times")
        self.rad_times.pack(side="left")
        self.ent_times = ctk.CTkEntry(rep1, width=50, justify="center")
        self.ent_times.insert(0, "1")
        self.ent_times.pack(side="right", padx=(5,0))
        
        rep2 = ctk.CTkFrame(frame_repeat, fg_color="transparent")
        rep2.pack(fill="x", padx=10, pady=5)
        self.rad_until = ctk.CTkRadioButton(rep2, text="Durdurulana kadar", variable=self.repeat_var, value="until_stopped")
        self.rad_until.pack(side="left", pady=(5,10))

        # 4. İmleç Konumu (Cursor Position)
        frame_pos = ctk.CTkFrame(self.tab_mouse)
        frame_pos.pack(pady=10, padx=10, fill="x")
        ctk.CTkLabel(frame_pos, text="İmleç Konumu", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=5)
        
        self.pos_var = ctk.StringVar(value="current")
        
        pos_row1 = ctk.CTkFrame(frame_pos, fg_color="transparent")
        pos_row1.pack(fill="x", padx=10, pady=5)
        self.rad_curr_pos = ctk.CTkRadioButton(pos_row1, text="Mevcut konum", variable=self.pos_var, value="current")
        self.rad_curr_pos.pack(side="left")
        
        pos_row2 = ctk.CTkFrame(frame_pos, fg_color="transparent")
        pos_row2.pack(fill="x", padx=10, pady=5)
        self.rad_pick_pos = ctk.CTkRadioButton(pos_row2, text="Konum Seç", variable=self.pos_var, value="picked")
        self.rad_pick_pos.pack(side="left")
        
        self.btn_pick = ctk.CTkButton(pos_row2, text="Seç", width=50, command=self.pick_mouse_location)
        self.btn_pick.pack(side="left", padx=10)
        
        ctk.CTkLabel(pos_row2, text="X:").pack(side="left")
        self.ent_x = ctk.CTkEntry(pos_row2, width=50, justify="center")
        self.ent_x.insert(0, "0")
        self.ent_x.pack(side="left", padx=5)
        
        ctk.CTkLabel(pos_row2, text="Y:").pack(side="left")
        self.ent_y = ctk.CTkEntry(pos_row2, width=50, justify="center")
        self.ent_y.insert(0, "0")
        self.ent_y.pack(side="left", padx=5)

        self.btn_apply_mouse = ctk.CTkButton(self.tab_mouse, text="Ayarları Uygula", command=self.apply_mouse_settings, fg_color="#E67E22", hover_color="#D35400")
        self.btn_apply_mouse.pack(pady=10)

    # --- SİSTEM & DİNLEYİCİ MANTIKLARI ---

    def setup_global_listener(self):
        keyboard.on_press(self._on_key_event)
        mouse.hook(self._on_mouse_event)

    def _on_key_event(self, event):
        # Sadece Klavye Tuşu Algılama (Seç Butonu İçin)
        if self.is_catching_key:
            self.is_catching_key = False
            self.after(0, self.append_to_keys, event.name)
            return

        if self.is_binding:
            self.is_binding = False
            self.after(0, self.update_hotkey, event.name)
            self.after(0, lambda: self.btn_bind.configure(text="Tuşu Değiştir", state="normal", fg_color="#3498DB"))
            return

        if event.name == self.hotkey_name:
            self.toggle_active_spammer()

    def _on_mouse_event(self, event):
        if isinstance(event, mouse.ButtonEvent) and event.event_type == 'down':
            if event.button == self.hotkey_name:
                self.toggle_active_spammer()

    def toggle_active_spammer(self):
        """Hangi sekme açıksa o sekmeye ait motoru tetikler."""
        current_tab = self.tabview.get()
        if current_tab == "Klavye":
            if self.mouse_backend.running: self.mouse_backend.stop()
            self.kbd_backend.toggle()
        elif current_tab == "Fare":
            if self.kbd_backend.running: self.kbd_backend.stop()
            self.mouse_backend.toggle()

    # --- KLAVYE SEKMESİ MANTIĞI ---

    def start_key_catch(self):
        if self.kbd_backend.running: self.kbd_backend.stop()
        self.btn_add_key.configure(text="Dinleniyor...", state="disabled", fg_color="#f39c12")
        # Fare tuşlarını algılamaması için artık sadece klavye dinliyoruz
        self.after(150, lambda: setattr(self, 'is_catching_key', True))

    def append_to_keys(self, new_val):
        self.ent_keys.delete(0, 'end')
        self.ent_keys.insert(0, new_val)
        self.btn_add_key.configure(text="Seç", state="normal", fg_color="#2ECC71")

    def apply_kbd_settings(self):
        keys = self.ent_keys.get()
        try: delay = float(self.ent_delay.get())
        except ValueError: delay = 0.1
        self.kbd_backend.set_params(keys, delay)

    # --- FARE SEKMESİ MANTIĞI ---

    def apply_mouse_settings(self):
        try:
            h = int(self.ent_h.get() or 0)
            m = int(self.ent_m.get() or 0)
            s = int(self.ent_s.get() or 0)
            ms = int(self.ent_ms.get() or 0)
            interval = (h * 3600) + (m * 60) + s + (ms / 1000.0)
            
            times = int(self.ent_times.get() or 1)
            pos_x = int(self.ent_x.get() or 0)
            pos_y = int(self.ent_y.get() or 0)
        except ValueError:
            return

        self.mouse_backend.set_params(
            interval=interval,
            button=self.cmb_btn.get(),
            click_type=self.cmb_type.get(),
            repeat_mode=self.repeat_var.get(),
            repeat_times=times,
            pos_mode=self.pos_var.get(),
            pos_x=pos_x,
            pos_y=pos_y
        )

    def pick_mouse_location(self):
        """Kullanıcı ekranda bir yere tıklayana kadar bekler ve X, Y'yi alır."""
        self.btn_pick.configure(text="...", state="disabled")
        self.pos_var.set("picked") # Konum Seç'i otomatik işaretle
        threading.Thread(target=self._wait_location_click, daemon=True).start()

    def _wait_location_click(self):
        time.sleep(0.2) # Butona basma olayının geçmesi için bekle
        while not mouse.is_pressed('left'):
            time.sleep(0.01)
        x, y = mouse.get_position()
        self.after(0, self._set_location_entries, x, y)

    def _set_location_entries(self, x, y):
        self.ent_x.delete(0, 'end')
        self.ent_x.insert(0, str(x))
        self.ent_y.delete(0, 'end')
        self.ent_y.insert(0, str(y))
        self.btn_pick.configure(text="Seç", state="normal")

    # --- ORTAK KISAYOL & PROFİL MANTIĞI ---

    def start_binding(self):
        if self.kbd_backend.running: self.kbd_backend.stop()
        if self.mouse_backend.running: self.mouse_backend.stop()
            
        self.btn_bind.configure(text="Basın...", state="disabled", fg_color="#f39c12")
        self.lbl_status.configure(text="YENİ TUŞ BEKLENİYOR", text_color="#f39c12")
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
                        self.after(0, self.update_hotkey, btn)
                        self.after(0, lambda: self.btn_bind.configure(text="Tuşu Değiştir", state="normal", fg_color="#3498DB"))
                        return
                except Exception: pass
            time.sleep(0.01)

    def update_hotkey(self, new_key):
        if self.kbd_backend.running: self.kbd_backend.stop()
        if self.mouse_backend.running: self.mouse_backend.stop()
                
        self.hotkey_name = new_key
        self.lbl_hotkey.configure(text=f"Kısayol: {self.hotkey_name.upper()}")
        self.update_status(False)

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
            self.update_hotkey(data.get("hotkey", "f8"))
            self.apply_kbd_settings()

    def save_current_profile(self):
        profile_name = self.cmb_profile.get().strip()
        if not profile_name: return
        self.profiles[profile_name] = {
            "keys": self.ent_keys.get(),
            "delay": self.ent_delay.get(),
            "hotkey": self.hotkey_name
        }
        self.save_profiles_to_file()
        self.cmb_profile.configure(values=list(self.profiles.keys()))
        self.apply_kbd_settings()

    def update_status(self, is_running):
        current_tab = self.tabview.get()
        if is_running:
            self.lbl_status.configure(text=f"ÇALIŞIYOR ({current_tab.upper()})", text_color="#2ecc71")
        else:
            self.lbl_status.configure(text="DURUYOR", text_color="#ff4c4c")

if __name__ == "__main__":
    app = SpammerUI()
    app.mainloop()