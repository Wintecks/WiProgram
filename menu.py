from PyQt5.QtWidgets import (
    QApplication, QSystemTrayIcon, QMenu, QAction, QStyle, QMainWindow
)
from settingmenu import open_setting_window


def open_menu(parent: QMainWindow, pos):
    """Контектне меню для вікна налаштування радіального меню"""
    item = parent.ui.TreeWidget.itemAt(pos)
    if not item:
        return

    menu = QMenu()

    if not item.parent():
        test_action = QAction("Test Action", parent)
        test_action.triggered.connect(lambda: parent.test_action(item))
        add_file = QAction("Add File", parent)
        add_file.triggered.connect(lambda: parent.add_action(item, "File"))
        add_folde = QAction("Add Foled", parent)
        add_folde.triggered.connect(
            lambda: parent.add_action(item, "Folder")
        )
        add_url = QAction("Add Url", parent)
        add_url.triggered.connect(lambda: parent.add_action(item, "Url"))
        add_macros = QAction("Add Macros", parent)
        add_macros.triggered.connect(
            lambda: parent.add_action(item, "Macros")
        )
        delete = QAction("Delete", parent)
        delete.triggered.connect(lambda: parent.del_item(item))

        menu.addAction(test_action)
        menu.addSeparator()
        menu.addActions([add_file, add_folde, add_url, add_macros])
        menu.addSeparator()
        menu.addAction(delete)
    else:
        delete_path = QAction("Delete", parent)
        delete_path.triggered.connect(lambda: parent.del_item(item))
        menu.addAction(delete_path)

    menu.exec_(parent.ui.TreeWidget.viewport().mapToGlobal(pos))


def tray(parent: QMainWindow):
    tray_icon = QSystemTrayIcon(parent)

    icon = parent.style().standardIcon(QStyle.SP_TitleBarMaxButton)
    tray_icon.setIcon(icon)

    tray_menu = QMenu()

    open_setting = QAction("Open Setting", parent)
    open_setting.triggered.connect(lambda: open_setting_window(parent))
    exit_action = QAction("Exit", parent)
    exit_action.triggered.connect(QApplication.instance().quit)

    tray_menu.addAction(open_setting)
    tray_menu.addSeparator()
    tray_menu.addAction(exit_action)

    tray_icon.setContextMenu(tray_menu)
    tray_icon.show()

    tray_icon.setToolTip("WiProgram")
