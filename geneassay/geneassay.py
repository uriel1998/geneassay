#!/usr/bin/env python3
# @1.1.0
# @name: Geneassay!
# @author: Dino Paulo R. Gomez 2024

import os
import json
import subprocess
import sys
import threading
import time
import venv
from datetime import datetime
from pathlib import Path

from urllib.parse import urlparse


def _in_virtualenv():
    return (
        sys.prefix != getattr(sys, "base_prefix", sys.prefix)
        or hasattr(sys, "real_prefix")
        or os.environ.get("VIRTUAL_ENV") is not None
    )


def _venv_python_path(venv_dir):
    if os.name == "nt":
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def _ensure_runtime_environment():
    project_root = Path(__file__).resolve().parent.parent
    requirements_path = project_root / "requirements.txt"
    venv_dir = project_root / ".venv"

    if not _in_virtualenv():
        if not venv_dir.exists():
            venv.create(venv_dir, with_pip=True)
        venv_python = _venv_python_path(venv_dir)
        os.execv(str(venv_python), [str(venv_python), str(Path(__file__).resolve()), *sys.argv[1:]])

    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "-r", str(requirements_path)],
        cwd=project_root,
    )


_ensure_runtime_environment()

from pypresence import Presence
from PIL import ImageTk
import customtkinter as ctk


PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"
PANIC_IMAGE_URL = "https://raw.githubusercontent.com/uriel1998/geneassay/master/panic.png"

# Dont really understand why, but it increases the render speed.
# Caught ibus to be getting most of the cpu% so quick read
# through github leads me to this fix.

# disable input methods to improve speed
# @https://github.com/ibus/ibus/issues/2324#issuecomment-996449177
os.environ['XMODIFIERS'] = "@im=none"

# App Constants
CONFIG = {
    "VERSION": "1.0.0",
    "AUTHOR": "Dino Paulo R. Gomez",
    "APP_TITLE": f"Geneassay: Discord Rich Presence",
    "APP_ICON": "assets/icon.png",
    "APP_LOGO": "assets/logo.png",
    "APP_GEOMETRY": "520x480",
    "APP_RESIZABLE_X": False,
    "APP_RESIZABLE_Y": False,
    "APP_DIMENSION": "520x520",
    "APP_FONT": ("Consolas", 12)
}

# Widget Coloring
STYLE = {
    "NORMAL": "#2fa572",
    "DISABLED": "#0e5637",
    "ENTRY": "#343638",
    "ENTRY_DISABLED": "#28292a",
    "ERROR": "red"
}


# Retrieves assets relpath
def resource_path(relative_path):
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(
        os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


# Checks for URL pattern
def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


# Discord Presence provided by pypresence
class DiscordRPC:
    def __init__(self):
        self.RPC = Presence(None)

    def connect(self, app_id):
        try:
            self.RPC = Presence(app_id)
            self.RPC.connect()
            self.RPC.update(state="Launching Geneassay 🚀",
                            details="A user is preparing his presence.", start=int(time.time()))
            return True, None
        except Exception as e:
            return False, e

    def test_connection(self, app_id):
        try:
            self.RPC = Presence(app_id)
            self.RPC.connect()
            self.RPC.close()
            return True, None
        except Exception as e:
            return False, e

    def disconnect(self):
        try:
            self.RPC.close()
            return True
        except:
            return False

    def update_presence(self, **kwargs):
        if not self.RPC:
            return False, "Discord RPC is not connected."

        presence = {}
        for key, value in kwargs.items():
            if value:
                presence[key] = value

        try:
            print("Args", presence)
            self.RPC.update(**presence)
            return True, None
        except Exception as e:
            return False, e


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Discord Presence
        self.discord_rpc = DiscordRPC()

        # Timestamp Timers
        self.start_time = time.time()
        self.update_timestamp = None
        self.selected_timestamp = None

        # App Configs
        ctk.set_default_color_theme("green")
        ctk.set_appearance_mode("dark")
        self.title(CONFIG["APP_TITLE"])
        self.geometry(CONFIG["APP_DIMENSION"])
        self.resizable(CONFIG["APP_RESIZABLE_X"], CONFIG["APP_RESIZABLE_Y"])

        # App Main Frame [Frame]
        self.frame = ctk.CTkFrame(master=self)
        self.frame.grid_columnconfigure((0, 1), weight=1)
        self.frame.pack(padx=10, pady=10, fill="x")

        # Config  [Label,Combobox, Button]@Grid
        self.label_config = ctk.CTkLabel(
            self.frame, text="Config", font=CONFIG["APP_FONT"])
        self.label_config.grid(row=0, column=0, padx=5, pady=5)
        self.config_list = []
        self.combobox_config = ctk.CTkComboBox(
            self.frame, values=self.config_list, command=self.combobox_config_callback)
        self.combobox_config.grid(
            row=0, column=1, columnspan=4, padx=5, pady=10, sticky="ew")

        self.combobox_config.set("Select Config")

        self.button_config = ctk.CTkButton(self.frame,  text="Save Config", font=(
            "Consolas", 12), command=self.save_config, width=110)
        self.button_config.grid(row=0, column=5, padx=3, sticky="we")

        # App [Label,Entry]@Grid
        self.label_app_id = ctk.CTkLabel(
            self.frame, text="App ID", font=CONFIG["APP_FONT"])
        self.label_app_id.grid(row=1, column=0, padx=5, pady=5)

        self.entry_app_id = ctk.CTkEntry(self.frame)
        self.entry_app_id.grid(
            row=1, column=1, columnspan=3, padx=5, pady=5, sticky="we")

        # Connect [Button:connect()]@Grid
        self.button_connect = ctk.CTkButton(self.frame, text="Connect", font=(
            "Consolas", 12), command=self.connect, width=110)
        self.button_connect.grid(row=1, column=4, padx=3, sticky="w")

        # Disconnect [Button:disconnect()]@Grid
        self.button_disconnect = ctk.CTkButton(self.frame, state="disabled", text="Disconnect", fg_color=STYLE["DISABLED"], font=(
            "Consolas", 12), command=self.disconnect, width=110)
        self.button_disconnect.grid(row=1, column=5, padx=3, sticky="we")

        # Details [Label,Entry]@Grid
        self.label_details = ctk.CTkLabel(
            self.frame, text="Details", font=CONFIG["APP_FONT"])
        self.label_details.grid(row=2, column=0, padx=5, pady=5)

        self.entry_details = ctk.CTkEntry(self.frame)
        self.entry_details.grid(
            row=2, column=1, columnspan=5, padx=5, pady=5, sticky="ew")

        # Party State [Label, Entry]@Grid
        self.label_party_state = ctk.CTkLabel(
            self.frame, text="State", font=CONFIG["APP_FONT"])
        self.label_party_state.grid(row=3, column=0, padx=5, pady=5)

        self.entry_party_state = ctk.CTkEntry(self.frame)
        self.entry_party_state.grid(row=3, column=1, columnspan=2,
                                    padx=5, pady=5, sticky="we")

        # Party [Label]@Grid
        self.label_party = ctk.CTkLabel(
            self.frame, text="Party", font=CONFIG["APP_FONT"], width=5)
        self.label_party.grid(row=3, column=3, padx=5, pady=5, sticky="w")

        # Party Min [Entry:validate_integer()]@Grid
        self.vcmd = (self.register(self.validate_integer), '%P')
        self.entry_party_min = ctk.CTkEntry(
            self.frame, validate="key", validatecommand=self.vcmd, width=90, placeholder_text=0)
        self.entry_party_min.grid(
            row=3, column=4, padx=(5, 25), pady=5, sticky="we")

        # Party Separator [Label]@Grid
        self.separator_label = ctk.CTkLabel(
            self.frame, text="of", font=CONFIG["APP_FONT"])
        self.separator_label.grid(row=3, column=4, padx=5, pady=5, sticky="e")

        # Party Max [Entry:validate_integer()]@Grid
        self.vcmd = (self.register(self.validate_integer), '%P')
        self.entry_party_max = ctk.CTkEntry(
            self.frame, validate="key", validatecommand=self.vcmd, width=10, placeholder_text=1)
        self.entry_party_max.grid(row=3, column=5, padx=5, pady=5, sticky="we")

        # Timestamp Dropdown Content
        self.timestamp_list = ["None", "Start Time",
                               "Last Update", "Local Time", "Custom Timestamp"]

        # Timestamp [Label, Combobox]@Grid
        self.label_timestamp = ctk.CTkLabel(
            self.frame, text="Timestamp", font=CONFIG["APP_FONT"])
        self.label_timestamp.grid(row=4, column=0, padx=5, pady=5)

        self.combobox_var = ctk.StringVar(
            value=self.timestamp_list[1])  # set initial value
        self.combobox_timestamp = ctk.CTkComboBox(self.frame,
                                                  values=self.timestamp_list,
                                                  command=self.combobox_timestamp_callback,
                                                  variable=self.combobox_var
                                                  )
        self.combobox_timestamp.grid(
            row=4, column=1, columnspan=2, padx=5, pady=5, sticky="we")

        # Custom Timestamp [Label,Entry]@Grid
        self.label_custom_timestamp = ctk.CTkLabel(
            self.frame, text="Custom", font=CONFIG["APP_FONT"], width=5)
        self.label_custom_timestamp.grid(
            row=4, column=3, padx=5, pady=5, sticky="w")

        self.entry_custom_timestamp = ctk.CTkEntry(
            self.frame, validate="key", state="disabled", fg_color=STYLE["ENTRY"])
        self.entry_custom_timestamp.grid(
            row=4, column=4, columnspan=3, padx=5, pady=5, sticky="we")

        # Large Image [Label]@Grid
        self.label_large_image = ctk.CTkLabel(
            self.frame, text="Large Image", font=CONFIG["APP_FONT"])
        self.label_large_image.grid(
            row=7, column=1, padx=5, pady=5, sticky="w")

        # Large Image URL [Entry]@Grid
        self.entry_large_image_url = ctk.CTkEntry(self.frame)
        self.entry_large_image_url.grid(
            row=8, column=1, columnspan=3, padx=5, pady=5, sticky="we")

        # Large Image Text [Entry]@Grid
        self.entry_large_image_text = ctk.CTkEntry(self.frame)
        self.entry_large_image_text.grid(
            row=9, column=1, columnspan=3, padx=5, pady=5, sticky="we")

        # Small Image [Label]@Grid
        self.label_small_image = ctk.CTkLabel(
            self.frame, text="Small Image", font=CONFIG["APP_FONT"])
        self.label_small_image.grid(
            row=7, column=4, padx=5, pady=5, sticky="w")

        # Small Image Url [Entry]@Grid
        self.entry_small_image_url = ctk.CTkEntry(self.frame)
        self.entry_small_image_url.grid(
            row=8, column=4, columnspan=3, padx=5, pady=5, sticky="we")

        # Small Image Text [Entry]@Grid
        self.entry_small_image_text = ctk.CTkEntry(self.frame)
        self.entry_small_image_text.grid(
            row=9, column=4, columnspan=3, padx=5, pady=5, sticky="we")

        # Image URL [Label]@Grid
        self.label_image_url = ctk.CTkLabel(
            self.frame, text="URL", font=CONFIG["APP_FONT"])
        self.label_image_url.grid(row=8, column=0, padx=5, pady=5)

        # Image Text [Label]@Grid
        self.label_image_text = ctk.CTkLabel(
            self.frame, text="Text", font=CONFIG["APP_FONT"])
        self.label_image_text.grid(row=9, column=0, padx=5, pady=5)

        # Button 1 [Label]@Grid
        self.label_button_one = ctk.CTkLabel(
            self.frame, text="Button 1", font=CONFIG["APP_FONT"])
        self.label_button_one.grid(
            row=10, column=1, padx=5, pady=5, sticky="w")

        # Button 1 Url [Entry]@Grid
        self.entry_button_one_url = ctk.CTkEntry(self.frame)
        self.entry_button_one_url.grid(
            row=11, column=1, columnspan=3, padx=5, pady=5, sticky="we")

        # Button 1 Text [Entry]@Grid
        self.entry_button_one_text = ctk.CTkEntry(self.frame)
        self.entry_button_one_text.grid(
            row=12, column=1, columnspan=3, padx=5, pady=5, sticky="we")

        # Button 2 [Label]@Grid
        self.label_button_two = ctk.CTkLabel(
            self.frame, text="Button 2", font=CONFIG["APP_FONT"])
        self.label_button_two.grid(
            row=10, column=4, padx=5, pady=5, sticky="w")

        # Button 2 Url [Entry]@Grid
        self.entry_button_two_url = ctk.CTkEntry(self.frame)
        self.entry_button_two_url.grid(
            row=11, column=4, columnspan=3, padx=5, pady=5, sticky="we")

        # Button 2 Text [Entry]@Grid
        self.entry_button_two_text = ctk.CTkEntry(self.frame)
        self.entry_button_two_text.grid(
            row=12, column=4, columnspan=3, padx=5, pady=5, sticky="we")

        # Button URL [Label]@Grid
        self.label_button_url = ctk.CTkLabel(
            self.frame, text="URL", font=CONFIG["APP_FONT"])
        self.label_button_url.grid(row=11, column=0, padx=5, pady=5)

        # Button Text [Label]@Grid
        self.label_button_text = ctk.CTkLabel(
            self.frame, text="TEXT", font=CONFIG["APP_FONT"])
        self.label_button_text.grid(row=12, column=0, padx=5, pady=5)

        # Update Presence [Button:update()]@Grid
        self.button_update = ctk.CTkButton(self.frame, state="disabled", fg_color=STYLE["DISABLED"], text="Update Presence", font=(
            "Consolas", 12), border_width=1, command=self.update)
        self.button_update.grid(
            row=13, column=0, columnspan=6, padx=5, pady=10, sticky="ew")

        # Connection State [Label]@Pack
        self.label_connection_state = ctk.CTkLabel(
            master=self, text="Disconnected", font=CONFIG["APP_FONT"],)
        self.label_connection_state.pack(padx=15, pady=(0, 5), side="right")

        # Error State [Label]@Pack
        self.label_app_state = ctk.CTkLabel(
            master=self, text="", font=CONFIG["APP_FONT"],)
        self.label_app_state.pack(pady=(0, 5), padx=15, side="left")

        # Vars
        self.isConnected = False
        self.isConnecting = False
        self.isSavingConfig = False
        self.isUpdatingPresence = False
        self.config_init()

    def combobox_config_callback(self, choice):
        print("combobox dropdown clicked:", choice)

        file_path = CONFIG_DIR / choice

        if not file_path.exists():
            self.set_app_label(f"Config file {choice} not found.", "red")
            return

        try:
            with file_path.open('r') as f:
                config_data = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            self.set_app_label("Error reading config file.", "red")
            return

        entry_fields = {
            "app_id": self.entry_app_id,
            "details": self.entry_details,
            "party_state": self.entry_party_state,
            "party_min": self.entry_party_min,
            "party_max": self.entry_party_max,
            "large_image_url": self.entry_large_image_url,
            "large_image_text": self.entry_large_image_text,
            "small_image_url": self.entry_small_image_url,
            "small_image_text": self.entry_small_image_text,
            "button_one_url": self.entry_button_one_url,
            "button_one_text": self.entry_button_one_text,
            "button_two_url": self.entry_button_two_url,
            "button_two_text": self.entry_button_two_text
        }

        for key, field in entry_fields.items():
            value = config_data.get(key, "")
            field.delete(0, ctk.END)
            field.insert(0, value)

        self.set_app_label(f"Loaded configuration {choice}.", "green")

    def config_init(self):
        CONFIG_DIR.mkdir(exist_ok=True)
        file_paths = sorted(CONFIG_DIR.glob("config_*.json"))

        if not file_paths:
            self.validate_and_set_app_label(True, "No config file loaded.")
        else:
            self.config_list.extend(file_path.name for file_path in file_paths)
            self.set_app_label(f"Loaded {len(file_paths)} configs.", "white")
            self.combobox_config.configure(values=self.config_list)

    def save_config(self):
        app_id = self.entry_app_id.get()
        if not app_id:
            self.set_app_label("A valid application id is required.", "red")
            return

        if self.isSavingConfig:
            self.set_app_label("Config save already in progress.")
            return

        self.isSavingConfig = True
        self.button_config.configure(
            state="disabled", fg_color=STYLE["DISABLED"])
        threading.Thread(
            target=self._save_config_async,
            args=(app_id,),
            daemon=True,
        ).start()

    def _save_config_async(self, app_id):
        success, error = self.discord_rpc.test_connection(app_id)
        if not success:
            self.after(0, self._finish_save_config, False, error, None)
            return

        print("Saving config...")
        config_data = {
            "app_id": app_id,
            "details": self.entry_details.get(),
            "party_state": self.entry_party_state.get(),
            "party_min": self.entry_party_min.get(),
            "party_max": self.entry_party_max.get(),
            "large_image_url": self.entry_large_image_url.get(),
            "large_image_text": self.entry_large_image_text.get(),
            "small_image_url": self.entry_small_image_url.get(),
            "small_image_text": self.entry_small_image_text.get(),
            "button_one_url": self.entry_button_one_url.get(),
            "button_one_text": self.entry_button_one_text.get(),
            "button_two_url": self.entry_button_two_url.get(),
            "button_two_text": self.entry_button_two_text.get()
        }

        # Filter out empty values
        config_data = {k: v for k, v in config_data.items() if v}

        file_name = f"config_{config_data['app_id']}.json"
        CONFIG_DIR.mkdir(exist_ok=True)
        file_path = CONFIG_DIR / file_name
        with file_path.open('w') as f:
            json.dump(config_data, f, indent=4)

        self.after(0, self._finish_save_config, True, None, file_name)

    def _finish_save_config(self, success, error, file_name):
        self.isSavingConfig = False
        self.button_config.configure(
            state="normal", fg_color=STYLE["NORMAL"])

        if not success:
            self.set_app_label(
                f"Config save failed. {self.format_error(error)}")
            return

        if file_name not in self.config_list:
            self.config_list.append(file_name)
        self.combobox_config.configure(values=self.config_list)
        self.set_app_label("Configuration saved successfully.", "green")

    def update(self):

        # Reset any existing error message
        self.set_app_label("")

        # Init
        self.timestamp = ""
        self.buttons = []

        # Fetch the values from the entries
        self.details = self.entry_details.get()
        self.party_state = self.entry_party_state.get()
        self.party_min = self.entry_party_min.get()
        self.party_max = self.entry_party_max.get()
        self.large_img_url = self.entry_large_image_url.get()
        self.large_img_txt = self.entry_large_image_text.get()
        self.small_img_url = self.entry_small_image_url.get()
        self.small_img_txt = self.entry_small_image_text.get()
        self.button_one_txt = self.entry_button_one_text.get()
        self.button_one_url = self.entry_button_one_url.get()
        self.button_two_txt = self.entry_button_two_text.get()
        self.button_two_url = self.entry_button_two_url.get()

        # Validate required fields for minimum length
        if self.validate_and_set_app_label(self.invalid_length(value=self.details), "Details needs 2 or more characters."):
            return
        if self.validate_and_set_app_label(self.invalid_length(value=self.party_state), "Party State needs 2 or more characters."):
            return
        if self.validate_and_set_app_label(self.invalid_length(value=self.large_img_txt), "Large Image Text needs 2 or more characters."):
            return
        if self.validate_and_set_app_label(self.invalid_length(value=self.small_img_txt), "Small Image Text needs 2 or more characters."):
            return

        # Validate party settings
        if self.party_min:
            if self.validate_and_set_app_label(not self.party_state, "Party number needs a state."):
                return
            if self.validate_and_set_app_label(not self.party_max, "Max is required."):
                return
            if self.validate_and_set_app_label(int(self.party_min) > int(self.party_max), "Min must not exceed Max"):
                return

        # Validate large image settings
        if self.validate_and_set_app_label(self.large_img_url and not self.large_img_txt, "Large Image URL requires Large Image Text."):
            return

        # Validate small image settings
        if self.validate_and_set_app_label(self.small_img_url and not self.small_img_txt, "Small Image URL requires Small Image Text."):
            return

        # Validate button settings
        if self.button_one_url:
            if self.button_one_txt:
                self.buttons.append(
                    {"url": self.button_one_url, "label": self.button_one_txt})
            else:
                self.set_app_label("Button 1 needs a label.")
                return

        if self.button_two_url:
            if self.button_two_txt:
                self.buttons.append(
                    {"url": self.button_two_url, "label": self.button_two_txt})
            else:
                self.set_app_label("Button 2 needs a label.")
                return

        # Parse custom timestamp if selected in combobox
        if self.combobox_timestamp.get() == self.timestamp_list[4]:
            custom_timestamp = self.entry_custom_timestamp.get(
            ).strip().replace('\n', '\\n').replace('\r', '\\r')
            if custom_timestamp:
                try:
                    dt = datetime.strptime(
                        custom_timestamp, "%B %d, %Y %I:%M:%S %p")
                    self.selected_timestamp = int(time.mktime(dt.timetuple()))
                except ValueError:
                    self.set_app_label("Invalid custom timestamp.")
                    return

        # Validate URLs
        urls_to_validate = {
            "Large Image Url": self.large_img_url,
            "Small Image Url": self.small_img_url,
            "Button One Url": self.button_one_url,
            "Button Two Url": self.button_two_url
        }

        for field_name, url in urls_to_validate.items():
            if url and not is_valid_url(url):
                self.set_app_label(f"Invalid {field_name}.")
                return

        # Prepare data for updating presence if connected
        if self.isConnected:
            update_kwargs = {}
            if self.details:
                update_kwargs["details"] = self.details
            if self.party_state:
                update_kwargs["state"] = self.party_state
            if self.large_img_url and self.large_img_txt:
                update_kwargs["large_image"] = self.large_img_url
                update_kwargs["large_text"] = self.large_img_txt
            if self.small_img_url and self.small_img_txt:
                update_kwargs["small_image"] = self.small_img_url
                update_kwargs["small_text"] = self.small_img_txt
            if self.buttons:
                update_kwargs["buttons"] = self.buttons
            if self.party_min and self.party_max:
                update_kwargs["party_size"] = [
                    int(self.party_min), int(self.party_max)]
            if self.selected_timestamp:
                update_kwargs["start"] = self.selected_timestamp
            if update_kwargs:
                if self.isUpdatingPresence:
                    self.set_app_label("Presence update already in progress.")
                    return

                self.isUpdatingPresence = True
                self.button_update.configure(
                    state="disabled", fg_color=STYLE["DISABLED"])
                threading.Thread(
                    target=self._update_presence_async,
                    args=(update_kwargs,),
                    daemon=True,
                ).start()

    def _update_presence_async(self, update_kwargs):
        success, error = self.discord_rpc.update_presence(**update_kwargs)
        used_fallback_images = False

        if not success and self._has_presence_images(update_kwargs):
            fallback_kwargs = self._with_fallback_images(update_kwargs)
            success, error = self.discord_rpc.update_presence(**fallback_kwargs)
            used_fallback_images = success

        self.after(
            0,
            self._finish_presence_update,
            success,
            error,
            used_fallback_images,
        )

    def _finish_presence_update(self, success, error, used_fallback_images):
        self.isUpdatingPresence = False

        if self.isConnected:
            self.button_update.configure(
                state="normal", fg_color=STYLE["NORMAL"])

        if success:
            self.update_timestamp = datetime.now().timestamp()
            if used_fallback_images:
                self.set_app_label(
                    "Presence updated using fallback image.", "white")
            else:
                self.set_app_label("Presence Updated", "white")
            return

        self.set_app_label(
            f"Presence update failed. {self.format_error(error)}")

    def _has_presence_images(self, update_kwargs):
        return bool(
            update_kwargs.get("large_image") or update_kwargs.get("small_image")
        )

    def _with_fallback_images(self, update_kwargs):
        fallback_kwargs = dict(update_kwargs)

        if fallback_kwargs.get("large_image"):
            fallback_kwargs["large_image"] = PANIC_IMAGE_URL
        if fallback_kwargs.get("small_image"):
            fallback_kwargs["small_image"] = PANIC_IMAGE_URL

        return fallback_kwargs

    def format_error(self, error):
        if error is None:
            return "Unknown error."

        message = getattr(error, "message", None)
        if message:
            return message

        return str(error)

    def connect(self):
        # Retrieve the Application ID entered by the user
        self.app_id = self.entry_app_id.get()

        # Validate the Application ID; if invalid, display an error and return
        if self.validate_and_set_app_label(not self.app_id, "Application ID is required."):
            return

        if self.isConnecting:
            self.set_app_label("Connection already in progress.")
            return

        self.isConnecting = True
        self.button_connect.configure(
            state="disabled", fg_color=STYLE["DISABLED"])
        self.set_app_label("Connecting...", "white")
        threading.Thread(
            target=self._connect_async,
            args=(self.app_id,),
            daemon=True,
        ).start()

    def _connect_async(self, app_id):
        success, result = self.discord_rpc.connect(app_id)
        self.after(0, self._finish_connect, success, result)

    def _finish_connect(self, success, result):
        self.isConnecting = False

        if success:
            # If connection is successful, update the connection state
            self.isConnected = True
            self.label_connection_state.configure(text="Connected")
            self.button_connect.configure(
                state="disabled", fg_color=STYLE["DISABLED"])
            self.button_disconnect.configure(
                state="normal", fg_color=STYLE["NORMAL"])
            self.button_update.configure(
                state="normal", fg_color=STYLE["NORMAL"])
            # Clear any previous error messages
            self.set_app_label("")
            return True

        self.button_connect.configure(
            state="normal", fg_color=STYLE["NORMAL"])
        self.set_app_label(
            f"Connection Failed. {self.format_error(result)}")

    def disconnect(self):
        # Check if already disconnected
        if not self.isConnected:
            return

        # Attempt to disconnect from Discord RPC
        if self.discord_rpc.disconnect():
            # Update connection status
            self.isConnected = False
            # Update UI elements to reflect disconnection
            self.label_connection_state.configure(text="Disconnected")
            self.button_connect.configure(
                state="normal", fg_color=STYLE["NORMAL"])
            self.button_disconnect.configure(
                state="disabled", fg_color=STYLE["DISABLED"])
            self.button_update.configure(
                state="disabled", fg_color=STYLE["DISABLED"])
            # Clear any existing error messages
            self.set_app_label("")

    def combobox_timestamp_callback(self, choice):
        # Disable the custom timestamp entry field if the selected choice is not the custom option
        if choice != self.timestamp_list[4]:
            self.entry_custom_timestamp.configure(
                state="disabled", fg_color=STYLE["ENTRY"])

        # Map the dropdown choices to corresponding timestamps
        timestamp_map = {
            self.timestamp_list[1]: self.start_time,  # Set to start time
            # Set to update timestamp
            self.timestamp_list[2]: self.update_timestamp,
            # Set to current time
            self.timestamp_list[3]: datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            self.timestamp_list[0]: None  # No timestamp
        }

        # Set the selected_timestamp based on the mapped value of the chosen option
        if choice in timestamp_map:
            self.selected_timestamp = timestamp_map[choice]
        # Enable the custom timestamp entry field if the selected choice is the custom option
        elif choice == self.timestamp_list[4]:
            self.entry_custom_timestamp.configure(
                state="normal",
                fg_color=STYLE["ENTRY"],
                placeholder_text=datetime.now().strftime(
                    "%B %d, %Y %I:%M:%S %p")  # Set placeholder to current time
            )

    def set_app_label(self, msg, color=STYLE["ERROR"]):
        # Display an error message in the label
        self.label_app_state
        self.label_app_state.configure(
            text=msg, text_color=color)

    def validate_and_set_app_label(self, condition, error_message):
        # Set error message if condition is true and return True, otherwise return False
        if condition:
            self.set_app_label(error_message)
            return True
        return False

    def validate_integer(self, P):
        # Check if the input string P is a valid non-negative integer
        if P == "":
            return True
        try:
            value = int(P)
            return value >= 0
        except ValueError:
            return False

    def invalid_length(self, value):
        # Check if the length of the input string value is exactly 1
        return len(value) == 1


if __name__ == "__main__":
    app = App()

    # App Icon
    iconpath = ImageTk.PhotoImage(file=resource_path("assets/geneassay.png"))
    app.wm_iconbitmap()
    app.iconphoto(False, iconpath)

    app.mainloop()
