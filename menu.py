from __future__ import annotations
from typing import TYPE_CHECKING

from PyQt5.QtWidgets import (
    QApplication, QSystemTrayIcon, QMenu, QAction, QStyle, QMainWindow
)
from PyQt5 import QtCore

if TYPE_CHECKING:
    from settingmenu import RadialMenuSetting
    from macroseditor import MacrosEditor


def setting_menu(parent: RadialMenuSetting, pos: QtCore.QPoint):
    """Контекcне меню для вікна налаштування радіального меню"""
    item = parent.ui.TreeWidget.itemAt(pos)
    if not item:
        return

    menu = QMenu()

    if not item.parent():
        test_action = QAction("Test Action", parent)
        test_action.triggered.connect(lambda: parent.test_action(item))
        setting_category_menu = QMenu("Setting category", parent)
        color = QAction("Corlor", parent)
        color.triggered.connect(lambda: parent.select_color(item))
        # =====================================================
        buildin_app_menu = QMenu("Build-In App", parent)
        wipainter = QAction("WiPainter v1.1", parent)
        wipainter.triggered.connect(
            lambda: parent.add_action(item, "App", "WiPeinter")
        )
        # =====================================================
        add_file = QAction("Add File", parent)
        add_file.triggered.connect(lambda: parent.add_action(item, "File"))
        add_folde = QAction("Add Directory", parent)
        add_folde.triggered.connect(
            lambda: parent.add_action(item, "Directory")
        )
        add_url = QAction("Add Url", parent)
        add_url.triggered.connect(lambda: parent.add_action(item, "Url"))
        add_macros = QAction("Add Macros", parent)
        add_macros.triggered.connect(
            lambda: parent.add_action(item, "Macros")
        )
        add_api = QAction("Add API", parent)
        add_api.triggered.connect(lambda: parent.add_action(item, "API"))
        # =====================================================
        delete = QAction("Delete", parent)
        delete.triggered.connect(lambda: parent.del_item(item))

        menu.addAction(test_action)
        menu.addSeparator()
        menu.addMenu(setting_category_menu)
        setting_category_menu.addActions([color])
        menu.addSeparator()
        menu.addMenu(buildin_app_menu)
        buildin_app_menu.addActions([wipainter])
        menu.addSeparator()
        menu.addActions([add_file, add_folde, add_url, add_macros, add_api])
        menu.addSeparator()
        menu.addAction(delete)
    else:
        edit_action = QAction("Edit", parent)
        edit_action.triggered.connect(lambda: parent.edit_action(item))
        delete_path = QAction("Delete", parent)
        delete_path.triggered.connect(lambda: parent.del_item(item))

        menu.addAction(edit_action)
        menu.addSeparator()
        menu.addAction(delete_path)

    menu.exec_(parent.ui.TreeWidget.viewport().mapToGlobal(pos))


def macros_menu(parent: MacrosEditor, pos: QtCore.QPoint):
    menu = QMenu()

    add_delay = QAction("Add Dalay (ms)", parent)
    add_delay.triggered.connect(parent.add_delay)
    add_key = QAction("Add Key", parent)
    add_key.triggered.connect(parent.add_key)

    menu.addActions([add_delay, add_key])
    menu.addSeparator()
    menu.addAction(parent.del_item_action)

    menu.exec_(parent.ui.TreeWidget.viewport().mapToGlobal(pos))


def tray(parent: QMainWindow):
    from settingmenu import open_setting_window
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
