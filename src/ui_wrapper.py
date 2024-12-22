import PyQt6.QtWidgets as widgets

import pyui.index
import pyui.firewall

class Index:
    def __init__(self, item: widgets.QWidget):
        self.ui = pyui.index.Ui_Form()
        self.ui.setupUi(item)
        # TODO: bug
        self.ui.Firewall_New.clicked.connect(lambda : self.on_firewall_new_click())
        self.ui.Firewall_Refresh.clicked.connect(self.on_firewall_refresh)

    def on_firewall_new_click(self):
        print("firewall new clicked")
        dialog = widgets.QDialog()
        Firewall(dialog)
        dialog.exec()

    def on_firewall_refresh(self):
        print("firewall refresh")

class Firewall:
    def __init__(self, item: widgets.QDialog):
        self.item = item
        self.ui = pyui.firewall.Ui_Form()
        self.ui.setupUi(self.item)
        self.ui.comboBox.clear()
        self.ui.comboBox.addItems(['personal', 'black', 'sys-net', 'sys-usb'])
        self.ui.cancel.clicked.connect(lambda : self.on_cancel())
        self.ui.add.clicked.connect(self.on_add)

    def on_cancel(self):
        print("cancel")
        self.item.reject()

    def on_add(self):
        print("add")