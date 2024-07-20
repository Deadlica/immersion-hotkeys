import tkinter
import tkinter.messagebox
import customtkinter
import asbplayer
import visual_novel as vn
import util
import psutil
import threading
import subprocess
import time
import re


customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")

ASBPLAYER = "ASBPLAYER"
VN = "VISUAL NOVEL"

class App(customtkinter.CTk):
    def __init__(self, title: str, width: int, height: int, icon_path: str, platform: str, settings_path: str = ".AJATT-Hotkeys"):
        super().__init__()

        if platform == "Windows":
            self.sharex_name = "ShareX.exe"
        elif platform == "Mac": # dunno what its called in Mac
            self.sharex_name = "ShareX.mc"
        elif platform == "Linux": # dunno what its called in Linux
            self.sharex_name = "ShareX"

        self.text_to_setting = {
            "Subtitles": asbplayer.SUBTITLE_KEY,
            "DeepL": asbplayer.DEEPL_KEY,
            "Record": vn.RECORD_KEY,
            "Screenshot": vn.SCREENSHOT_KEY,
            "Audio": vn.AUDIO_KEY
        }

        self.pid = -1
        self.hotkey_window = None

        self.title(title)
        self.resizable(False, False)
        self.SETTINGS_PATH = settings_path
        self.WIDTH = width
        self.HEIGHT = height
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = int(screen_width / 2 - self.WIDTH / 2)
        y = int(screen_height / 2 - self.HEIGHT / 2)
        asbplayer.center_pos = (x + int(self.WIDTH / 2), y + int(self.HEIGHT / 2))
        vn.center_pos = asbplayer.center_pos
        self.geometry(f"{width}x{height}+{x}+{y}")

        self.ICON_PATH = icon_path
        self.iconbitmap(default=icon_path)

        self.main_frame = customtkinter.CTkFrame(master=self)
        self.main_frame.pack(pady=20, padx=20, fill="both", expand=True)
        self.__load_main_frame()


    def __clear_frame(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()


    def __load_main_frame(self):
        self.__clear_frame()
        asbplayer.remove_hotkeys()
        vn.remove_hotkeys()

        self.asb_mode = False
        self.vn_mode = False

        self.process_search = threading.Event()
        self.thread = threading.Thread(target=self.__worker, daemon=True)
        self.thread.start()

        self.hotkeys = {}
        self.coords = {}

        self.label = customtkinter.CTkLabel(master=self.main_frame, text="Choose Immersion")
        self.label.pack(pady=20, padx=10)

        self.asbplayer_button = customtkinter.CTkButton(master=self.main_frame, text="ASBPlayer", command=self.__load_asbplayer_frame)
        self.asbplayer_button.pack(pady=40, padx=10)

        self.vn_button = customtkinter.CTkButton(master=self.main_frame, text="Visual Novel", command=self.__load_vn_frame)
        self.vn_button.pack(pady=40, padx=10)


    def __load_asbplayer_frame(self):
        self.__clear_frame()
        self.asb_mode = True
        coords1, coords2, coords3 = asbplayer.load_coords(self.SETTINGS_PATH)
        sub_key, deepl_key = asbplayer.load_hotkeys(self.SETTINGS_PATH)
        self.hotkeys.update({asbplayer.SUBTITLE_KEY: sub_key})
        self.hotkeys.update({asbplayer.DEEPL_KEY: deepl_key})
        self.coords.update({asbplayer.SUBTITLE_COORD: coords1})
        self.coords.update({asbplayer.FOCUS_COORD: coords2})
        self.coords.update({asbplayer.DEEPL_COORD: coords3})
        coords1 = coords1.split(",")
        coords2 = coords2.split(",")
        coords3 = coords3.split(",")

        label = customtkinter.CTkLabel(master=self.main_frame, text="ASBPlayer")
        label.pack(pady=12, padx=10)

        button_pad = 30

        back_button = customtkinter.CTkButton(master=self.main_frame, text="Back", command=self.__load_main_frame)
        back_button.pack(side=tkinter.BOTTOM, pady=20, padx=10)

        hotkey_button = customtkinter.CTkButton(master=self.main_frame, text="Hotkey Settings", command=lambda: self.__load_hotkey_window("Subtitles", "DeepL", ASBPLAYER))
        hotkey_button.pack(side=tkinter.BOTTOM, pady=20, padx=10)

        subtitle_frame = customtkinter.CTkFrame(master=self.main_frame)
        subtitle_frame.pack(side=tkinter.LEFT, padx=button_pad)
        subtitle_button = customtkinter.CTkButton(master=subtitle_frame, text="Subtitle location", command=lambda: self.__register_coords(asbplayer.SUBTITLE_COORD, subtitle_label, ASBPLAYER))
        subtitle_button.pack()
        subtitle_label = customtkinter.CTkLabel(master=subtitle_frame, text=f"(x: {coords1[0]}, y: {coords1[1]})")
        subtitle_label.pack()

        focus_frame = customtkinter.CTkFrame(master=self.main_frame)
        focus_frame.pack(side=tkinter.LEFT, padx=button_pad)
        focus_button = customtkinter.CTkButton(master=focus_frame, text="ASBPlayer location", command=lambda: self.__register_coords(asbplayer.FOCUS_COORD, focus_label, ASBPLAYER))
        focus_button.pack()
        focus_label = customtkinter.CTkLabel(master=focus_frame, text=f"(x: {coords2[0]}, y: {coords2[1]})")
        focus_label.pack()

        deepl_frame = customtkinter.CTkFrame(master=self.main_frame)
        deepl_frame.pack(side=tkinter.LEFT, padx=button_pad)
        deepl_button = customtkinter.CTkButton(master=deepl_frame, text="DeepL location", command=lambda: self.__register_coords(asbplayer.DEEPL_COORD, deepl_label, ASBPLAYER))
        deepl_button.pack()
        deepl_label = customtkinter.CTkLabel(master=deepl_frame, text=f"(x: {coords3[0]}, y: {coords3[1]})")
        deepl_label.pack()


    def __load_vn_frame(self):
        if self.pid < 0:
            self.__show_custom_error("ShareX Error", "Please ensure ShareX is started!")
            return
        try:
            process = psutil.Process(self.pid)
        except:
            return
        if not process or process.name() != self.sharex_name:
            self.__show_custom_error("ShareX Error", "Please ensure ShareX is started!")
            return
        self.__clear_frame()
        self.vn_mode = True
        coords1, coords2, coords3, coords4 = vn.load_coords(self.SETTINGS_PATH)
        rec_key, deepl_key, screenshot_key, audio_key = vn.load_hotkeys(self.SETTINGS_PATH)
        tag, toggled = vn.load_tag(self.SETTINGS_PATH)
        self.hotkeys.update({vn.RECORD_KEY: rec_key})
        self.hotkeys.update({vn.DEEPL_KEY: deepl_key})
        self.hotkeys.update({vn.SCREENSHOT_KEY: screenshot_key})
        self.hotkeys.update({vn.AUDIO_KEY: audio_key})
        self.coords.update({vn.VN_COORD: coords1})
        self.coords.update({vn.AUDIO_COORD: coords2})
        self.coords.update({vn.STOP_COORD: coords3})
        self.coords.update({vn.DEEPL_COORD: coords4})
        coords1 = coords1.split(",")
        coords2 = coords2.split(",")
        coords3 = coords3.split(",")
        coords4 = coords4.split(",")

        label = customtkinter.CTkLabel(master=self.main_frame, text="Visual Novel")
        label.pack(pady=12, padx=10)

        button_pad = 5

        back_button = customtkinter.CTkButton(master=self.main_frame, text="Back", command=self.__load_main_frame)
        back_button.pack(side=tkinter.BOTTOM, pady=20, padx=10)

        hotkey_button = customtkinter.CTkButton(master=self.main_frame, text="Hotkey Settings", command=lambda: self.__load_hotkey_window("Record", "DeepL", VN, "Screenshot", "Audio"))
        hotkey_button.pack(side=tkinter.BOTTOM, pady=20, padx=10)

        def toggle_tag():
            if checked.get():
                tag_field.pack(side=tkinter.BOTTOM, pady=10)
                tag, tmp = vn.load_tag(self.SETTINGS_PATH)
                vn.tag = tag
                tag_text.set(tag)
            else:
                vn.tag = ""
                tag_field.pack_forget()
                vn.save_tag(tag_text.get(), False, self.SETTINGS_PATH)

        def on_tag_change(*args):
            vn.tag = tag_text.get()
            vn.save_tag(vn.tag, checked.get(), self.SETTINGS_PATH)

        tag_frame = customtkinter.CTkFrame(master=self.main_frame, fg_color="transparent")
        tag_frame.pack(side=tkinter.BOTTOM, pady=10, padx=10)
        checked = customtkinter.BooleanVar()
        tag_check = customtkinter.CTkCheckBox(master=tag_frame, text="Custom Tag", variable=checked, command=toggle_tag)
        tag_check.pack(side=tkinter.TOP)
        tag_text = customtkinter.StringVar()
        tag_text.trace_add("write", on_tag_change)
        tag_field = customtkinter.CTkEntry(master=tag_frame, placeholder_text="", placeholder_text_color="gray80", textvariable=tag_text)
        checked.set(toggled)
        if toggled:
            toggle_tag()

        vn_frame = customtkinter.CTkFrame(master=self.main_frame)
        vn_frame.pack(side=tkinter.LEFT, padx=button_pad)
        vn_button = customtkinter.CTkButton(master=vn_frame, text="VN location", command=lambda: self.__register_coords(vn.VN_COORD, vn_label, VN))
        vn_button.pack()
        vn_label = customtkinter.CTkLabel(master=vn_frame, text=f"(x: {coords1[0]}, y: {coords1[1]})")
        vn_label.pack()

        audio_frame = customtkinter.CTkFrame(master=self.main_frame)
        audio_frame.pack(side=tkinter.LEFT, padx=button_pad)
        audio_button = customtkinter.CTkButton(master=audio_frame, text="Audio location", command=lambda: self.__register_coords(vn.AUDIO_COORD, audio_label, VN))
        audio_button.pack()
        audio_label = customtkinter.CTkLabel(master=audio_frame, text=f"(x: {coords2[0]}, y: {coords2[1]})")
        audio_label.pack()

        stop_frame = customtkinter.CTkFrame(master=self.main_frame)
        stop_frame.pack(side=tkinter.LEFT, padx=button_pad)
        stop_button = customtkinter.CTkButton(master=stop_frame, text="Stop location", command=lambda: self.__register_coords(vn.STOP_COORD, stop_label, VN))
        stop_button.pack()
        stop_label = customtkinter.CTkLabel(master=stop_frame, text=f"(x: {coords3[0]}, y: {coords3[1]})")
        stop_label.pack()

        deepl_frame = customtkinter.CTkFrame(master=self.main_frame)
        deepl_frame.pack(side=tkinter.LEFT, padx=button_pad)
        deepl_button = customtkinter.CTkButton(master=deepl_frame, text="DeepL location", command=lambda: self.__register_coords(vn.DEEPL_COORD, deepl_label, VN))
        deepl_button.pack()
        deepl_label = customtkinter.CTkLabel(master=deepl_frame, text=f"(x: {coords4[0]}, y: {coords4[1]})")
        deepl_label.pack()


    def __load_hotkey_window(self, button1_text: str, button2_text: str, mode: str, button3_text: str = "", button4_text: str = ""):
        self.hotkey_window = customtkinter.CTkToplevel(self)
        asbplayer.remove_hotkeys()
        vn.remove_hotkeys()
        hotkeys = self.hotkeys.copy()
        width = int(self.WIDTH / 2)
        if mode == ASBPLAYER:
            height = int(self.HEIGHT / 2)
        elif mode == VN:
            height = int(self.HEIGHT / 1.7)
        parent_x = self.winfo_x()
        parent_y = self.winfo_y()
        parent_y = self.winfo_y()
        parent_width = self.winfo_width()
        parent_height = self.winfo_height()
        x = parent_x + (parent_width // 2) - (width // 2)
        y = parent_y + (parent_height // 2) - (height // 2)
        self.hotkey_window.geometry(f"{width}x{height}+{x}+{y}")

        self.hotkey_window.attributes("-topmost", True)
        self.hotkey_window.overrideredirect(True)
        self.hotkey_window.grab_set()

        bw = 4

        border_frame = customtkinter.CTkFrame(self.hotkey_window, border_width=bw, border_color="gray")
        border_frame.pack(fill="both", expand=True)

        title_bar = customtkinter.CTkFrame(master=border_frame, height=30)
        title_bar.pack(fill="x", pady=bw, padx=bw)
        title_label = customtkinter.CTkLabel(title_bar, text="Hotkey Settings")
        title_label.pack(side=tkinter.LEFT, padx=bw)

        bottom_frame = customtkinter.CTkFrame(master=border_frame, fg_color="transparent")
        bottom_frame.pack(side=tkinter.BOTTOM, pady=bw, padx=bw)
        ok_button = customtkinter.CTkButton(master=bottom_frame, text="Ok", command=lambda: self.__save_hotkeys(self.hotkey_window, hotkeys, mode))
        ok_button.pack(side=tkinter.LEFT, pady=20, padx=10)
        cancel_button = customtkinter.CTkButton(master=bottom_frame, text="Cancel", command=lambda: self.__save_hotkeys(self.hotkey_window, self.hotkeys, mode))
        cancel_button.pack(side=tkinter.LEFT, pady=20, padx=10)

        hotkey_frame = customtkinter.CTkFrame(master=border_frame, fg_color="transparent")
        hotkey_frame.pack(side=tkinter.TOP, pady=bw, padx=bw)
        button1_id = ""
        button2_id = ""
        if mode == ASBPLAYER:
            button1_id = asbplayer.SUBTITLE_KEY
            button2_id = asbplayer.DEEPL_KEY
        if mode == VN:
            button1_id = vn.RECORD_KEY
            button2_id = vn.DEEPL_KEY
            button3_id = vn.SCREENSHOT_KEY
            button4_id = vn.AUDIO_KEY
        button1 = customtkinter.CTkButton(master=hotkey_frame, text=button1_text + f" ({self.hotkeys[button1_id]})", command=lambda: self.__register_hotkey(self.hotkey_window, button1, button1_text, hotkeys))
        button1.pack(side=tkinter.LEFT, pady=20, padx=10)
        button2 = customtkinter.CTkButton(master=hotkey_frame, text=button2_text + f" ({self.hotkeys[button2_id]})", command=lambda: self.__register_hotkey(self.hotkey_window, button2, button2_text, hotkeys))
        button2.pack(side=tkinter.LEFT, pady=20, padx=10)

        if mode == VN:
            sharex_hotkey_frame = customtkinter.CTkFrame(master=border_frame, fg_color="transparent")
            sharex_hotkey_frame.pack(side=tkinter.TOP, pady=bw, padx=bw)
            button3 = customtkinter.CTkButton(master=sharex_hotkey_frame, text="Screenshot" + f" ({self.hotkeys[button3_id]})", command=lambda: self.__register_hotkey(self.hotkey_window, button3, button3_text, hotkeys))
            button3.pack(side=tkinter.LEFT, pady=0, padx=10)
            button4 = customtkinter.CTkButton(master=sharex_hotkey_frame, text="Audio" + f" ({self.hotkeys[button4_id]})", command=lambda: self.__register_hotkey(self.hotkey_window, button4, button4_text, hotkeys))
            button4.pack(side=tkinter.LEFT, pady=0, padx=10)


    def __register_hotkey(self, window: customtkinter.CTkToplevel, button: customtkinter.CTkButton, label: str, hotkeys: dict):
        keys = util.record_key_sequence()
        key_string = ""
        if len(keys) == 2:
            key_string = keys[0] + "+" + keys[1]
        else:
            key_string = keys[0]

        hotkeys[self.text_to_setting[label]] = key_string
        button.configure(text=label + " (" + key_string + ")")


    def __save_hotkeys(self, window: customtkinter.CTkToplevel, hotkeys: dict, mode: str):
        self.hotkeys = hotkeys
        if mode == ASBPLAYER:
            asbplayer.save_hotkeys(self.hotkeys, self.SETTINGS_PATH)
        elif mode == VN:
            vn.save_hotkeys(self.hotkeys, self.SETTINGS_PATH)
        window.destroy()


    def __register_coords(self, button: str, label: customtkinter.CTkLabel, mode: str):
        coord = util.get_click_position()
        coord = [str(coord[0]), str(coord[1])]
        label.configure(text="(x: "+ coord[0] + ", y: " + coord[1] + ")")
        self.coords[button] = coord[0] + "," + coord[1]
        if mode == ASBPLAYER:
            asbplayer.save_coords(self.coords, self.SETTINGS_PATH)
        elif mode == VN:
            vn.save_coords(self.coords, self.SETTINGS_PATH)
    

    def __worker(self):
        while True:
            self.pid = self.__get_process_id(self.sharex_name)
            if self.vn_mode and self.pid == -1:
                if self.hotkey_window:
                    self.after(0, self.hotkey_window.destroy)
                    self.hotkey_window = None
                self.after(0, self.__load_main_frame)
                self.after(0, lambda: self.__show_custom_error("ShareX Error", "ShareX has been closed!\n\n Please start ShareX to use 'Visual Novel' mode,"))
            time.sleep(1)


    def __get_process_id(self, process_name: str):
        progs = subprocess.run(['tasklist'], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW).stdout
        pattern = re.compile(rf'{process_name}\s+(\d+)\s+')
        match = pattern.search(progs)
        if match:
            return int(match.group(1))
        else:
            return -1


    def __show_custom_error(self, title, message):
        error_window = customtkinter.CTkToplevel(self, fg_color="gray10")
        error_window.title(title)
        width = int(self.WIDTH / 2)
        height = int(self.HEIGHT / 2)
        parent_x = self.winfo_x()
        parent_y = self.winfo_y()
        parent_y = self.winfo_y()
        parent_width = self.winfo_width()
        parent_height = self.winfo_height()
        x = parent_x + (parent_width // 2) - (width // 2)
        y = parent_y + (parent_height // 2) - (height // 2)
        error_window.geometry(f"{width}x{height}+{x}+{y}")

        error_window.attributes("-topmost", True)
        error_window.overrideredirect(True)
        error_window.grab_set()

        label = customtkinter.CTkLabel(master=error_window, text=message, wraplength=280, fg_color="red")
        label.pack(pady=20)

        button = customtkinter.CTkButton(master=error_window, text="OK", command=error_window.destroy)
        button.pack(pady=10)
    

    def start(self):
        self.mainloop()