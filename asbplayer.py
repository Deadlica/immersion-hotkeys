import pyautogui
import keyboard
import time
import os
import util


coord_file = "asbplayer_coords.dat"
key_file = "asbplayer_keys.dat"
center_pos = ()
subtitle_pos = ()
focus_pos = ()
deepl_pos = ()
subtitle_id = None
deepl_id = None
delay = 0.1
SUBTITLE_KEY = "subtitle_key"
DEEPL_KEY = "deepl_key"
SUBTITLE_COORD = "subtitle_coord"
FOCUS_COORD = "focus_coord"
DEEPL_COORD = "deepl_coord"


def click_subtitle():
    pyautogui.moveTo(subtitle_pos)
    time.sleep(delay)
    pyautogui.click()
    pyautogui.moveTo(center_pos)


def click_deepl():
    global deepl_pos
    global focus_pos
    global center_pos
    pyautogui.click(deepl_pos)
    pyautogui.hotkey('ctrl', 'v')
    pyautogui.moveTo(focus_pos)
    time.sleep(delay)
    pyautogui.click()
    pyautogui.moveTo(center_pos)


def load_coords(settings_path: str):
    global subtitle_pos
    global deepl_pos
    global focus_pos
    coords_file_path = settings_path + os.sep + coord_file
    util.ensure_settings_file_exist(coords_file_path, "subtitle_coord=0,0\nfocus_coord=0,0\ndeepl_coord=0,0")

    coords = ["", "", ""]
    with open(coords_file_path, "r") as file:
        for line in file:
            param, val = line.strip().split("=")
            val = val.split(",")
            if param == "subtitle_coord":
                coords[0] = val[0] + "," + val[1]
                subtitle_pos = (int(val[0]), int(val[1]))
            elif param == "focus_coord":
                coords[1] = val[0] + "," + val[1]
                focus_pos = (int(val[0]), int(val[1]))
            elif param == "deepl_coord":
                coords[2] = val[0] + "," + val[1]
                deepl_pos = (int(val[0]), int(val[1]))

    return coords


def load_hotkeys(settings_path: str):
    global subtitle_id
    global deepl_id
    if subtitle_id:
        keyboard.remove_hotkey(subtitle_id)
    if deepl_id:
        keyboard.remove_hotkey(deepl_id)
    keys_file_path = settings_path + os.sep + key_file
    util.ensure_settings_file_exist(keys_file_path, SUBTITLE_KEY + "=s\n" + DEEPL_KEY + "=t")

    keys = ["", ""]
    with open(keys_file_path, "r") as file:
        for line in file:
            param, val = line.strip().split("=")
            if param == SUBTITLE_KEY:
                keys[0] = val
            elif param == DEEPL_KEY:
                keys[1] = val

    subtitle_id = keyboard.add_hotkey(keys[0], click_subtitle)
    deepl_id = keyboard.add_hotkey(keys[1], click_deepl)
    return keys


def save_coords(coords: dict, settings_path: str):
    global subtitle_pos
    global focus_pos
    global deepl_pos
    coords_file_path = settings_path + os.sep + coord_file
    util.ensure_settings_file_exist(coords_file_path, "subtitle_coord=0,0\nfocus_coord=0,0\ndeepl_coord=0,0")
    content = {}
    with open(coords_file_path, "r") as file:
        for line in file:
            param, val = line.strip().split("=")
            content.update({param: val})

    for key, val in coords.items():
        if content.get(key):
            content[key] = val

    file = open(coords_file_path, "w")
    for i, (key, val) in enumerate(content.items()):
        file.write(key + "=" + val)
        if i < len(content) - 1:
            file.write("\n")
        if key == SUBTITLE_COORD:
            c = val.split(",")
            subtitle_pos = (int(c[0]), int(c[1]))
        elif key == FOCUS_COORD:
            c = val.split(",")
            focus_pos = (int(c[0]), int(c[1]))
        elif key == DEEPL_COORD:
            c = val.split(",")
            deepl_pos = (int(c[0]), int(c[1]))
    file.close()


def save_hotkeys(hotkeys: dict, settings_path: str):
    global subtitle_id
    global deepl_id
    if subtitle_id:
        keyboard.remove_hotkey(subtitle_id)
    if deepl_id:
        keyboard.remove_hotkey(deepl_id)
    keys_file_path = settings_path + os.sep + key_file
    util.ensure_settings_file_exist(keys_file_path, SUBTITLE_KEY + "=s\n" + DEEPL_KEY + "=t")
    content = {}
    with open(keys_file_path, "r") as file:
        for line in file:
            param, val = line.strip().split("=")
            content.update({param: val})

    for key, val in hotkeys.items():
        if content.get(key):
            content[key] = val

    file = open(keys_file_path, "w")
    for i, (key, val) in enumerate(content.items()):
        file.write(key + "=" + val)
        if i < len(content) - 1:
            file.write("\n")
        if key == SUBTITLE_KEY:
            subtitle_id = keyboard.add_hotkey(val, click_subtitle)
        elif key == DEEPL_KEY:
            deepl_id = keyboard.add_hotkey(val, click_deepl)
    file.close()


def remove_hotkeys():
    global subtitle_id
    global deepl_id
    if subtitle_id:
        keyboard.remove_hotkey(subtitle_id)
        subtitle_id = None
    if deepl_id:
        keyboard.remove_hotkey(deepl_id)
        deepl_id = None