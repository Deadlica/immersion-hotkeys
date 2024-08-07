import pyautogui
import keyboard
import time
import os
import util


coord_file = ".visual_novel_coords.dat"
key_file = ".visual_novel_keys.dat"
tag_file = ".visual_novel_tag.dat"
center_pos = ()
vn_pos = ()
audio_pos = ()
stop_pos = ()
deepl_pos = ()
record_id = None
deepl_id = None
screenshot_key = ""
audio_key = ""
delay = 1.0
tag = ""
RECORD_KEY = "record_key"
DEEPL_KEY = "deepl_key"
SCREENSHOT_KEY = "screenshot_key"
AUDIO_KEY = "audio_key"
VN_COORD = "vn_coord"
AUDIO_COORD = "audio_coord"
STOP_COORD = "stop_coord"
DEEPL_COORD = "deepl_coord"


def save_img_and_audio():
    pyautogui.hotkey(screenshot_key)
    time.sleep(delay)
    pyautogui.click(center_pos)
    time.sleep(2 * delay)
    pyautogui.hotkey(audio_key)
    time.sleep(0.2)
    pyautogui.click(audio_pos)
    pyautogui.moveTo(stop_pos)
    global tag
    if len(tag) > 0:
        time.sleep(delay)
        util.add_tag_to_lastest_card(tag)


def click_deepl():
    pyautogui.click(deepl_pos)
    pyautogui.hotkey('ctrl', 'v')
    pyautogui.moveTo(center_pos)


def load_coords(settings_path: str):
    global vn_pos
    global audio_pos
    global stop_pos
    global deepl_pos
    coords_file_path = settings_path + os.sep + coord_file
    util.ensure_settings_file_exist(coords_file_path, VN_COORD + "=0,0\n" + AUDIO_COORD + "=0,0\n" + STOP_COORD + "=0,0\n" + DEEPL_COORD + "=0,0")

    coords = ["", "", "", ""]
    with open(coords_file_path, "r") as file:
        for line in file:
            param, val = line.strip().split("=")
            val = val.split(",")
            if param == VN_COORD:
                coords[0] = val[0] + "," + val[1]
                vn_pos = (int(val[0]), int(val[1]))
            elif param == AUDIO_COORD:
                coords[1] = val[0] + "," + val[1]
                audio_pos = (int(val[0]), int(val[1]))
            elif param == STOP_COORD:
                coords[2] = val[0] + "," + val[1]
                stop_pos = (int(val[0]), int(val[1]))
            elif param == DEEPL_COORD:
                coords[3] = val[0] + "," + val[1]
                deepl_pos = (int(val[0]), int(val[1]))

    return coords


def load_hotkeys(settings_path: str):
    global record_id
    global deepl_id
    global screenshot_key
    global audio_key
    if record_id:
        keyboard.remove_hotkey(record_id)
    if deepl_id:
        keyboard.remove_hotkey(deepl_id)
    keys_file_path = settings_path + os.sep + key_file
    util.ensure_settings_file_exist(keys_file_path, RECORD_KEY + "=r\n" + DEEPL_KEY + "=t\n" + SCREENSHOT_KEY + "=F6\n" + AUDIO_KEY + "=F7")

    keys = ["", "", "", ""]
    with open(keys_file_path, "r") as file:
        for line in file:
            param, val = line.strip().split("=")
            if param == RECORD_KEY:
                keys[0] = val
            elif param == DEEPL_KEY:
                keys[1] = val
            elif param == SCREENSHOT_KEY:
                keys[2] = val
                screenshot_key = val
            elif param == AUDIO_KEY:
                keys[3] = val
                audio_key = val

    record_id = keyboard.add_hotkey(keys[0], save_img_and_audio)
    deepl_id = keyboard.add_hotkey(keys[1], click_deepl)
    return keys


def save_coords(coords: dict, settings_path: str):
    global vn_pos
    global audio_pos
    global stop_pos
    global deepl_pos
    coords_file_path = settings_path + os.sep + coord_file
    util.ensure_settings_file_exist(coords_file_path, VN_COORD + "=0,0\n" + AUDIO_COORD + "=0,0\n" + STOP_COORD + "=0,0\n" + DEEPL_COORD + "=0,0")
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
        if key == VN_COORD:
            c = val.split(",")
            vn_pos = (int(c[0]), int(c[1]))
        elif key == AUDIO_COORD:
            c = val.split(",")
            audio_pos = (int(c[0]), int(c[1]))
        elif key == STOP_COORD:
            c = val.split(",")
            stop_pos = (int(c[0]), int(c[1]))
        elif key == DEEPL_COORD:
            c = val.split(",")
            deepl_pos = (int(c[0]), int(c[1]))
    file.close()


def save_hotkeys(hotkeys: dict, settings_path: str):
    global record_id
    global deepl_id
    global screenshot_key
    global audio_key
    if record_id:
        keyboard.remove_hotkey(record_id)
    if deepl_id:
        keyboard.remove_hotkey(deepl_id)
    keys_file_path = settings_path + os.sep + key_file
    util.ensure_settings_file_exist(keys_file_path, RECORD_KEY + "=r\n" + DEEPL_KEY + "=t\n" + SCREENSHOT_KEY + "=F6\n" + AUDIO_KEY + "=F7")
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
        if key == RECORD_KEY:
            record_id = keyboard.add_hotkey(val, save_img_and_audio)
        elif key == DEEPL_KEY:
            deepl_id = keyboard.add_hotkey(val, click_deepl)
        elif key == SCREENSHOT_KEY:
            screenshot_key = val
        elif key == AUDIO_KEY:
            audio_key = val
    file.close()



def remove_hotkeys():
    global record_id
    global deepl_id
    if record_id:
        keyboard.remove_hotkey(record_id)
        record_id = None
    if deepl_id:
        keyboard.remove_hotkey(deepl_id)
        deepl_id = None


def load_tag(settings_path: str):
    tag_file_path = settings_path + os.sep + tag_file
    util.ensure_settings_file_exist(tag_file_path, "False\n")

    tag = ""
    toggled = ""
    with open(tag_file_path, "r") as file:
        toggled = file.readline().strip()
        tag = file.readline().strip()

    if toggled == "True":
        toggled = True
    elif toggled == "False":
        toggled = False
    return tag, toggled


def save_tag(tag: str, toggled: bool, settings_path: str):
    tag_file_path = settings_path + os.sep + tag_file
    util.ensure_settings_file_exist(tag_file_path, "False\n")

    file = open(tag_file_path, "w")
    file.write(str(toggled) + "\n")
    file.write(tag)
    file.close()