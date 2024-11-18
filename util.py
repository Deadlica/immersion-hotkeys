import keyboard
from pynput import mouse
import os
import requests
import json
import pyautogui


anki_url = "http://127.0.0.1:8765"


headers = {
    'Content-Type': 'application/json; charset=UTF-8'
}


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
            mouse_pos = pyautogui.position()
            position.append((mouse_pos.x, mouse_pos.y))
            return False

    with mouse.Listener(on_click=on_click) as listener:
        listener.join()

    return position[0] if position else None


def ensure_settings_file_exist(path: str, default_settings: str):
    if not os.path.isfile(path):
        file = open(path, "w")
        file.write(default_settings)
        file.close()


def get_latest_note_id():
    body_find_note = {
        "action": "findNotes",
        "version": 6,
        "params": {
            "query": "added:1"
        }
    }
    response_find_notes = requests.post(anki_url, headers=headers, data=json.dumps(body_find_note))
    if response_find_notes.status_code == 200:
        response_json = response_find_notes.json()
        data_result = response_json.get('result', [])
        sorted_list = sorted(data_result, key=lambda x: int(x), reverse=True)
        if sorted_list:
            return sorted_list[0]
        else:
             return None
    else:
         return "BAD RESPONSE"


def add_tag_to_lastest_card(tag: str):
    note_id = get_latest_note_id()
    if note_id == None or note_id == "BAD RESPONSE":
        return note_id

    body_add_tag = {
        "action": "addTags",
        "version": 6,
        "params": {
            "notes": [note_id],
            "tags": tag
        }
    }

    response_add_tags = requests.post(anki_url, headers=headers, data=json.dumps(body_add_tag))
    if response_add_tags.status_code == 200:
        return True
    return False