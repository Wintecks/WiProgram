import os
import webbrowser
import json
from time import sleep

import requests
from PyQt5.QtWidgets import QApplication
from pynput import keyboard, mouse

from build_in_app.wipeinter import WiPainter
from classes import APIResponseView


keyboards = keyboard.Controller()
mouses = mouse.Controller()
app_ = None


def active_action(selected_option, actions):
    global app_
    """Активація дії"""
    print(f"Виконую: {selected_option}")
    for action in actions[selected_option]["actions"]:
        type_ = action["type"]
        match type_:
            case "Directory" | "File":
                os.startfile(action["data"])
            case "Url":
                webbrowser.open(action["data"])
            case "Macros":
                for item in action["data"]:
                    if not isinstance(item, dict):
                        continue
                    data = item["data"]
                    match item["action"]:
                        case "Key Press":
                            keyboards.press(data.split("'")[1])
                        case "Key Release":
                            keyboards.release(data.split("'")[1])
                        case "Mouse Down":
                            btn, x, y = data.split(",")
                            mouses.position = (int(x), int(y))
                            mouses.press(
                                getattr(mouse.Button, btn.split(".")[1])
                            )
                        case "Mouse Up":
                            btn, x, y = data.split(",")
                            mouses.position = (int(x), int(y))
                            mouses.release(
                                getattr(mouse.Button, btn.split(".")[1])
                            )
                        case "Delay":
                            sleep(int(data) / 1000.0)
            case "App":
                match action["data"]:
                    case "WiPeinter":
                        app_ = WiPainter()
                        app_.show()
            case "API":
                data = action["data"]
                api_data = {}
                if os.path.isfile(data["data"]):
                    with open(api_data, "r", encoding="utf-8") as file:
                        api_data = json.load(file)
                else:
                    if data["data"]:
                        api_data = json.loads(data["data"])

                if data["getfromclipboard"]["enabled"]:
                    api_data.update({
                        data["getfromclipboard"]["key"]:
                        QApplication.clipboard().text()
                    })

                if data["type"] == "Get":
                    response = requests.get(data["url"], api_data).json()

                    if data["filter"]["enabled"]:
                        filter_values = data["filter"]["value"]
                        if data["filter"]["type"] == "Index":
                            filter_values = [
                                int(v) for v in filter_values
                                if v.strip().isdigit()
                            ]

                        if isinstance(response, list):
                            if data["filter"]["listtype"] == "White":
                                response = [
                                    response[i] for i in filter_values
                                ]
                            else:
                                response = [
                                    v for i, v in enumerate(response)
                                    if i not in filter_values
                                ]
                        elif isinstance(response, dict):
                            filter_set = set(map(str, filter_values))
                            if data["filter"]["listtype"] == "White":
                                response = {
                                    k: v for k, v in response.items()
                                    if k in filter_set
                                }
                            else:
                                response = {
                                    k: v for k, v in response.items()
                                    if k not in filter_set
                                }
                    if data["copytoclipboard"]:
                        QApplication.clipboard().setText(
                            str(response).replace("'", '"')
                        )
                    if data["windowout"]:
                        dialog = APIResponseView(response, action["path"])
                        dialog.exec_()
                    if data["savetofile"]["enabled"]:
                        with open(
                            data["savetofile"]["path"], "w", encoding="utf-8"
                        ) as file:
                            json.dump(
                                response, file, ensure_ascii=False, indent=4
                            )
                else:
                    requests.post(data["url"], json=api_data)
