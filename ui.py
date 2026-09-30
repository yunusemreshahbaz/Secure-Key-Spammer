import customtkinter as ctk
from engines import KeyboardEngine, MouseEngine
from profile_manager import ProfileManager
from input_manager import InputManager

class SpammerUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("MC AutoKey & Clicker")
        self.geometry("520x650")
        self.resizable(False, False)
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # 1. DEPENDENCY INJECTION (Sınıfların Başlatılması)
        self.kbd_engine = KeyboardEngine(self.update_status)
        self.mouse_engine = MouseEngine(self.update_status)
        self.profile_manager = ProfileManager()
        self.input_manager = InputManager()
        
        # 2. EVENT BINDING (Arka plandan arayüze veri aktarımı)
        # .after(0, ...) kullanımı Thread çatışmalarını engeller
        self.input_manager.on_toggle = lambda: self.after(0, self.toggle_active_spammer)
        self.input_manager.on_key_caught = lambda key: self.after(0, self._on_key_caught, key)
        self.input_manager.on_hotkey_bound = lambda key: self.after(0, self._on_hotkey_bound, key)
        self.input_manager.setup_listeners()

        self.setup_ui()
        self.load_initial_profile()

    # ==========================================
    # UI WIDGET KURULUMLARI
    # ==========================================
    def setup_ui(self):
        self.tabview = ctk.CTkTabview(self, width=480, height=480)
        self.tabview.pack(pady=(10, 5), padx=20, fill="both", expand=True)
        
        self.tab_kbd = self.tabview.add("Klavye")
        self.tab_mouse = self.tabview.add("Fare")

        self.setup_keyboard_tab()
        self.setup_mouse_tab()

        self.frame_bottom = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_bottom.pack(pady=5, padx=20, fill="x")
        
        self.lbl_status = ctk.CTkLabel(self.frame_bottom, text="DURUYOR", text_color="#ff4c4c", font=("Arial", 18, "bold"))
        self.lbl_status.pack(pady=5)
        
        self.frame_hotkey = ctk.CTkFrame(self.frame_bottom, fg_color="#2b2b2b", corner_radius=10)
        self.frame_hotkey.pack(pady=5, fill="x", ipadx=10, ipady=10)
        
        self.lbl_hotkey = ctk.CTkLabel(self.frame_hotkey, text=f"Kısayol: {self.input_manager.hotkey_name.upper()}", font=("Arial", 14, "bold"))
        self.lbl_hotkey.pack(side="left", padx=15)
        
        self.btn_bind = ctk.CTkButton(self.frame_hotkey, text="Tuşu Değiştir", width=120, fg_color="#3498DB", hover_color="#2980B9", command=self.start_binding)
        self.btn_bind.pack(side="right", padx=15)

    def setup_keyboard_tab(self):
        frame_profile = ctk.CTkFrame(self.tab_kbd)
        frame_profile.pack(pady=(10, 15), padx=10, fill="x")

        ctk.CTkLabel(frame_profile, text="Profil Seç / Yeni İsim Yaz:", font=("Arial", 12)).pack(pady=(10, 0))
        
        profile_names = self.profile_manager.get_all_names() or ["Varsayılan"]
        self.cmb_profile = ctk.CTkComboBox(frame_profile, values=profile_names, command=self.on_profile_selected)
        self.cmb_profile.pack(pady=5, padx=10, fill="x")

        ctk.CTkButton(frame_profile, text="Ayarları Kaydet", command=self.save_current_profile).pack(pady=(0, 10), padx=10, fill="x")

        ctk.CTkLabel(self.tab_kbd, text="Spamlanacak Tuş:", font=("Arial", 12, "bold")).pack(pady=(10, 0))
        
        frame_keys = ctk.CTkFrame(self.tab_kbd, fg_color="transparent")
        frame_keys.pack(pady=5)
        
        self.ent_keys = ctk.CTkEntry(frame_keys, width=150, placeholder_text="Örn: w, 1", justify="center")
        self.ent_keys.pack(side="left", padx=5)
        
        self.btn_add_key = ctk.CTkButton(frame_keys, text="Seç", width=60, fg_color="#2ECC71", hover_color="#27AE60", command=self.start_key_catch)
        self.btn_add_key.pack(side="left")

        ctk.CTkLabel(self.tab_kbd, text="Gecikme (Saniye):", font=("Arial", 12, "bold")).pack(pady=(15, 0))
        self.ent_delay = ctk.CTkEntry(self.tab_kbd, width=150, justify="center")
        self.ent_delay.insert(0, "0.1")
        self.ent_delay.pack(pady=5)

        self.btn_apply_kbd = ctk.CTkButton(self.tab_kbd, text="Ayarları Uygula", command=self.apply_kbd_settings, fg_color="#E67E22", hover_color="#D35400")
        self.btn_apply_kbd.pack(pady=20)

    def setup_mouse_tab(self):
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

        frame_middle = ctk.CTkFrame(self.tab_mouse, fg_color="transparent")
        frame_middle.pack(pady=5, padx=10, fill="x")

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

        frame_repeat = ctk.CTkFrame(frame_middle, width=200)
        frame_repeat.pack(side="right", fill="both", expand=True, padx=(5, 0))
        ctk.CTkLabel(frame_repeat, text="Tekrar Modu", font=("Arial", 12, "bold")).pack(anchor="w", padx=10, pady=5)
        
        self.repeat_var = ctk.StringVar(value="until_stopped")
        
        rep1 = ctk.CTkFrame(frame_repeat, fg_color="transparent")
        rep1.pack(fill="x", padx=10, pady=5)
        self.rad_times = ctk.CTkRadioButton(rep1, text="Kere:", variable=self.repeat_var, value="times")
        self.rad_times.pack(side="left")
        self.ent_times = ctk.CTkEntry(rep1, width=50, justify="center")
        self.ent_times.insert(0, "1")
        self.ent_times.pack(side="right", padx=(5,0))
        
        rep2 = ctk.CTkFrame(frame_repeat, fg_color="transparent")
        rep2.pack(fill="x", padx=10, pady=5)
        self.rad_until = ctk.CTkRadioButton(rep2, text="Sürekli", variable=self.repeat_var, value="until_stopped")
        self.rad_until.pack(side="left", pady=(5,10))

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

    # ==========================================
    # LOGIC - KONTROLÖR METOTLARI
    # ==========================================
    def toggle_active_spammer(self):
        current_tab = self.tabview.get()
        if current_tab == "Klavye":
            if self.mouse_engine.running: self.mouse_engine.stop()
            self.kbd_engine.toggle()
        elif current_tab == "Fare":
            if self.kbd_engine.running: self.kbd_engine.stop()
            self.mouse_engine.toggle()

    def update_status(self, is_running):
        current_tab = self.tabview.get()
        if is_running:
            self.lbl_status.configure(text=f"ÇALIŞIYOR ({current_tab.upper()})", text_color="#2ecc71")
        else:
            self.lbl_status.configure(text="DURUYOR", text_color="#ff4c4c")

    def start_key_catch(self):
        if self.kbd_engine.running: self.kbd_engine.stop()
        self.btn_add_key.configure(text="Dinleniyor...", state="disabled", fg_color="#f39c12")
        self.input_manager.start_key_catch()

    def _on_key_caught(self, new_val):
        self.ent_keys.delete(0, 'end')
        self.ent_keys.insert(0, new_val)
        self.btn_add_key.configure(text="Seç", state="normal", fg_color="#2ECC71")

    def start_binding(self):
        if self.kbd_engine.running: self.kbd_engine.stop()
        if self.mouse_engine.running: self.mouse_engine.stop()
        self.btn_bind.configure(text="Basın...", state="disabled", fg_color="#f39c12")
        self.lbl_status.configure(text="YENİ TUŞ BEKLENİYOR", text_color="#f39c12")
        self.input_manager.start_binding()

    def _on_hotkey_bound(self, new_key):
        self.input_manager.set_hotkey(new_key)
        self.lbl_hotkey.configure(text=f"Kısayol: {new_key.upper()}")
        self.btn_bind.configure(text="Tuşu Değiştir", state="normal", fg_color="#3498DB")
        self.update_status(False)

    def pick_mouse_location(self):
        self.btn_pick.configure(text="...", state="disabled")
        self.pos_var.set("picked")
        self.input_manager.wait_for_location_click(lambda x, y: self.after(0, self._set_location_entries, x, y))

    def _set_location_entries(self, x, y):
        self.ent_x.delete(0, 'end')
        self.ent_x.insert(0, str(x))
        self.ent_y.delete(0, 'end')
        self.ent_y.insert(0, str(y))
        self.btn_pick.configure(text="Seç", state="normal")

    def load_initial_profile(self):
        names = self.profile_manager.get_all_names()
        if names:
            first = names[0]
            self.cmb_profile.set(first)
            self.on_profile_selected(first)

    def on_profile_selected(self, choice):
        data = self.profile_manager.get_profile(choice)
        if not data: return
        
        self.ent_keys.delete(0, 'end')
        self.ent_keys.insert(0, data.get("keys", ""))
        self.ent_delay.delete(0, 'end')
        self.ent_delay.insert(0, str(data.get("delay", "0.1")))
        
        hotkey = data.get("hotkey", "f8")
        self._on_hotkey_bound(hotkey)
        self.apply_kbd_settings()

    def save_current_profile(self):
        name = self.cmb_profile.get().strip()
        if not name: return
        
        data = {
            "keys": self.ent_keys.get(),
            "delay": self.ent_delay.get(),
            "hotkey": self.input_manager.hotkey_name
        }
        self.profile_manager.add_or_update(name, data)
        self.cmb_profile.configure(values=self.profile_manager.get_all_names())
        self.apply_kbd_settings()

    def apply_kbd_settings(self):
        keys = self.ent_keys.get()
        try: delay = float(self.ent_delay.get())
        except ValueError: delay = 0.1
        self.kbd_engine.set_params(keys, delay)

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
        except ValueError: return

        self.mouse_engine.set_params(
            interval=interval, button=self.cmb_btn.get(), click_type=self.cmb_type.get(),
            repeat_mode=self.repeat_var.get(), repeat_times=times,
            pos_mode=self.pos_var.get(), pos_x=pos_x, pos_y=pos_y
        )