from PyQt5.QtWidgets import QApplication, QDialog, QFileDialog

from ui.dialog.Ui_ApiEdit import Ui_APIEdit

from functions import active_action


class APIEditor(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_APIEdit()
        self.ui.setupUi(self)

        self.ui.TypeURL.currentIndexChanged.connect(
            self.ui.stackedWidget.setCurrentIndex
        )

        self.ui.ButtonTest.clicked.connect(self.test)
        self.ui.ButtonSelectFile_Post.clicked.connect(self.select_file)
        self.ui.ButtonSelectFile_Get.clicked.connect(self.save_to_file)

    def test(self):
        data = self.getValues()
        active_action(
            "test", {
                "test": [
                    {
                        "path": data.pop("name"),
                        "type": "API",
                        "content": data
                    }
                ]
            }
        )

    def select_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Select file", self.ui.LineData.text(),
            "Json (*.json);;All File(*.*)"
        )
        if path:
            self.ui.LineData.setText(path)

    def save_to_file(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Select to save file", self.ui.LineFilePath.text(),
            "Json (*.json);;All File(*.*)"
        )

        if path:
            self.ui.LineFilePath.setText(path)

    def setValue(self, data: dict, name: str):
        self.ui.LineAPIUrl.setText(data["url"])
        self.ui.TypeURL.setCurrentText(data["type"])
        self.ui.LineName.setText(name)

        if data["type"] == "Get":
            self.ui.GetFromClipboad_Get.setChecked(
                data["getfromclipboard"]["enabled"]
            )
            self.ui.LineKey_Get.setText(data["getfromclipboard"]["key"])
            self.ui.LineDataJson.setText(data["data"])

            self.ui.CupyToClipboard.setChecked(data["copytoclipboard"])
            self.ui.Window.setChecked(data["windowout"])

            self.ui.SaveToFile.setChecked(data["savetofile"]["enabled"])
            self.ui.LineFilePath.setText(data["savetofile"]["path"])

            self.ui.Fileter.setChecked(data["filter"]["enabled"])
            self.ui.FilterListType.setCurrentText(data["filter"]["listtype"])
            self.ui.FilterType.setCurrentText(data["filter"]["type"])
            self.ui.LineFileter.setText(", ".join(data["filter"]["value"]))
        else:
            self.ui.GetFormClipboard_Post.setChecked(
                data["getfromclipboard"]["enabled"]
            )
            self.ui.LineKey_Post.setText(data["getfromclipboard"]["key"])
            self.ui.LineData.setText(data["data"])

    def getValues(self):
        if self.ui.TypeURL.currentText() == "Get":
            data = {
                "name": self.ui.LineName.text(),
                "type": self.ui.TypeURL.currentText(),
                "url": self.ui.LineAPIUrl.text(),
                "getfromclipboard": {
                    "enabled": self.ui.GetFromClipboad_Get.isChecked(),
                    "key": self.ui.LineKey_Get.text()
                },
                "data": self.ui.LineDataJson.text(),
                "copytoclipboard": self.ui.CupyToClipboard.isChecked(),
                "windowout": self.ui.Window.isChecked(),
                "savetofile": {
                    "enabled": self.ui.SaveToFile.isChecked(),
                    "path": self.ui.LineFilePath.text()
                },
                "filter": {
                    "enabled": self.ui.Fileter.isChecked(),
                    "listtype": self.ui.FilterListType.currentText(),
                    "type": self.ui.FilterType.currentText(),
                    "value": [
                        t.strip()
                        for t in self.ui.LineFileter.text().split(",")
                    ]
                }
            }
        else:
            data = {
                "name": self.ui.LineName.text(),
                "type": self.ui.TypeURL.currentText(),
                "url": self.ui.LineAPIUrl.text(),
                "getfromclipboard": {
                    "enabled": self.ui.GetFormClipboard_Post.isChecked(),
                    "key": self.ui.LineKey_Post.text()
                },
                "data": self.ui.LineData.text()
            }
        return data


if __name__ == "__main__":
    app = QApplication([])
    window = APIEditor()
    window.show()
    app.exec()
    print(window.getValues())
