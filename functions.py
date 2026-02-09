import os
import webbrowser
from pynput import keyboard

keyboards = keyboard.Controller()

def active_action(selected_option, actions):
    print(actions)
    print(f"Виконую: {selected_option}")
    for action in actions[selected_option]:
        type_ = action["type"]
        match type_:
            case "Folder" | "File":
                os.startfile(action["path"])
            case "Url":
                webbrowser.open(action["path"])
            case "Macros":
                run_macros(action['content'])

def run_macros(content):
    for item in content:
        if not isinstance(item, dict):
            continue
        datals = item["datals"].split("'")[1]
        match item['action']:
            case "Key Press":
                keyboards.press(datals)
            case "Key Release":
                keyboards.release(datals)