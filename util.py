import keyboard
from pynput import mouse
import os


key_name_map = {
    "shift": ["shift", "skift"],
    "right shift": ["right shift", "right skift"],
    "ctrl": ["ctrl", "control"],
    "right ctrl": ["right ctrl", "right control", "höger crtl"],
    "alt": ["alt"],
    "right alt": ["right alt", "alt gr", "höger alt"],
    "down" : ["nedpil"],
    "left" : ["vänsterpil"],
    "up" : ["uppil"],
    "right" : ["högerpil"]
}


combo_keys = [
    "shift",
    "right shift",
    "ctrl",
    "right ctrl",
    "alt",
    "right alt"
]


def normalize_key_name(key: str):
    for standard_name, variants in key_name_map.items():
        if key.lower() in variants:
            return standard_name
    return key


def record_key_sequence():
    keys = []
    two_keys = False

    key = normalize_key_name(keyboard.read_key())
    keys.append(key)
    while key in combo_keys:
        key = normalize_key_name(keyboard.read_key())
        two_keys = True

    if two_keys:
        keys.append(key.lower())
    return keys


def get_click_position():
    position = []

    def on_click(x, y, button, pressed):
        if pressed and button == mouse.Button.left:
            position.append((x, y))
            return False

    with mouse.Listener(on_click=on_click) as listener:
        listener.join()

    return position[0] if position else None


def ensure_settings_file_exist(path: str, default_settings: str):
    if not os.path.isfile(path):
        file = open(path, "w")
        file.write(default_settings)
        file.close()