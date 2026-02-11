import os
import webbrowser

from pynput import keyboard

from build_in_app.wipeinter import WiPainter


keyboards = keyboard.Controller()
wi_painter = None


def active_action(selected_option, actions):
    """Активація дії"""
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
            case "App":
                run_app(action["path"])


def run_app(app):
    global wi_painter
    match app:
        case "WiPeinter":
            wi_painter = WiPainter()
            wi_painter.show()


def run_macros(content):
    """Запуск макросу"""
    for item in content:
        if not isinstance(item, dict):
            continue
        datals = item["datals"].split("'")[1]
        match item['action']:
            case "Key Press":
                keyboards.press(datals)
            case "Key Release":
                keyboards.release(datals)
