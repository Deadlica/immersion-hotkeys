import os
from app import *

settings_path = ".AJATT-Hotkeys"
icon_path = "sonic.ico"
TITLE = "AJATT Hotkeys"

def resource_path(relative_path: str):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

if __name__ == "__main__":
    if not os.path.isdir(settings_path):
        os.makedirs(settings_path)

    app = App(TITLE, 600, 400, resource_path(icon_path))
    app.start()
