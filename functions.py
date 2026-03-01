import os
import webbrowser
import json

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
    for action in actions[selected_option]:
        type_ = action["type"]
        match type_:
            case "Folder" | "File":
                os.startfile(action["path"])
            case "Url":
                webbrowser.open(action["path"])
            case "Macros":
                for item in action["content"]:
                    if not isinstance(item, dict):
                        continue
                    datals = item["datals"]
                    match item["action"]:
                        case "Key Press":
                            keyboards.press(datals.split("'")[1])
                        case "Key Release":
                            keyboards.release(datals.split("'")[1])
                        case "Mouse Down":
                            btn, x, y = datals.split(",")
                            mouses.position = (int(x), int(y))
                            mouses.press(
                                getattr(mouse.Button, btn.split(".")[1])
                            )
                        case "Mouse Up":
                            btn, x, y = datals.split(",")
                            mouses.position = (int(x), int(y))
                            mouses.release(
                                getattr(mouse.Button, btn.split(".")[1])
                            )
            case "App":
                match action["path"]:
                    case "WiPeinter":
                        app_ = WiPainter()
                        app_.show()
            case "API":
                data = action["content"]
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
