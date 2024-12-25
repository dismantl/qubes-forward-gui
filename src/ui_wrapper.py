import PyQt6.QtWidgets as widgets

from config import config
import pyui.forward
import pyui.index
import pyui.firewall
import utils

class Index:
    def __init__(self, item: widgets.QWidget):
        self.ui = pyui.index.Ui_Form()
        self.ui.setupUi(item)
        
        # forward
        self.ui.PortForwarding_New.clicked.connect(lambda : self.on_port_forward_new())
        self.ui.PortForwarding_Refresh.clicked.connect(self.on_port_forward_refresh)

        # firewall
        self.ui.Firewall_New.clicked.connect(self.on_firewall_new_click)
        self.ui.Firewall_Refresh.clicked.connect(self.on_firewall_refresh)

        # fix some ui issues
        # self.ui.textBrowser.setOpenExternalLinks(True)
        self.ui.tableWidget.setColumnWidth(0, 30)
        self.ui.tableWidget_2.setColumnWidth(0, 30)

        # show rules
        self.on_port_forward_refresh()
        self.on_firewall_refresh()

    def on_port_forward_new(self):
        config.logger.debug("port forward new")
        
        dialog = widgets.QDialog()
        Forward(dialog)
        dialog.exec()
        
        # update rules after adding new rule
        self.on_port_forward_refresh()

    def on_port_forward_refresh(self):
        config.logger.debug("port forward refresh")
        rules = utils.get_forward_rules()
        self.ui.tableWidget.setRowCount(0)
        
        for row, rule in enumerate(rules):
            self.ui.tableWidget.insertRow(row)
            
            delete_button = widgets.QPushButton("D")
            delete_button.clicked.connect(lambda _, row=row, rule_id=rule.id: self.on_port_forward_delete(row, rule_id))
            
            self.ui.tableWidget.setCellWidget(row, 0, delete_button)
            self.ui.tableWidget.setItem(row, 1, widgets.QTableWidgetItem(rule.from_qube))
            self.ui.tableWidget.setItem(row, 2, widgets.QTableWidgetItem(str(rule.from_port)))
            self.ui.tableWidget.setItem(row, 3, widgets.QTableWidgetItem(rule.to_qube))
            self.ui.tableWidget.setItem(row, 4, widgets.QTableWidgetItem(str(rule.to_port)))
            self.ui.tableWidget.setItem(row, 5, widgets.QTableWidgetItem(str(rule.pid)))

    def on_port_forward_delete(self, row: int, rule_id: int):
        config.logger.debug(f"delete rule {rule_id}")
        self.ui.tableWidget.removeRow(row)
        utils.delete_forward_rule(rule_id)
        self.on_port_forward_refresh()

    def on_firewall_new_click(self):
        config.logger.debug("firewall new clicked")
        dialog = widgets.QDialog()
        Firewall(dialog)
        dialog.exec()
        self.on_firewall_refresh()

    def on_firewall_refresh(self):
        config.logger.debug("firewall refresh")
        rules = utils.get_firewall_rules()
        
        self.ui.tableWidget_2.setRowCount(0)
        for row, rule in enumerate(rules):
            self.ui.tableWidget_2.insertRow(row)
            
            delete_button = widgets.QPushButton("D")
            delete_button.clicked.connect(lambda _, row=row, rule_id=rule.id: self.on_firewall_rule_delete(row, rule_id))
            
            self.ui.tableWidget_2.setCellWidget(row, 0, delete_button)
            self.ui.tableWidget_2.setItem(row, 1, widgets.QTableWidgetItem(rule.qube))
            self.ui.tableWidget_2.setItem(row, 2, widgets.QTableWidgetItem(str(rule.port)))

    def on_firewall_rule_delete(self, row: int, rule_id: int):
        config.logger.debug(f"delete rule {rule_id}")
        self.ui.tableWidget.removeRow(row)
        utils.delete_firewall_rule(rule_id)
        self.on_firewall_refresh()

class Forward:
    def __init__(self, item: widgets.QDialog):
        def combobox_changed():
            selected_qube = self.ui.comboBox.currentText()
            allowed_qubes = [n for n in names if n != selected_qube]
            self.ui.comboBox_2.clear()
            self.ui.comboBox_2.addItems(allowed_qubes)
            
        self.item = item
        self.ui = pyui.forward.Ui_Form()
        self.ui.setupUi(self.item)
        
        running = utils.get_qubes_running()
        names = [q.name for q in running]
        
        self.ui.comboBox.clear()
        self.ui.comboBox.addItems(names)
        self.ui.comboBox.currentTextChanged.connect(combobox_changed)
        combobox_changed()

        self.ui.pushButton_2.clicked.connect(lambda : self.on_cancel())
        self.ui.pushButton.clicked.connect(self.on_add)
    
    def on_cancel(self):
        config.logger.debug("cancel")
        self.item.reject()
    
    def on_add(self):
        from_qube = self.ui.comboBox.currentText()
        from_port = self.ui.spinBox.text()
        to_qube = self.ui.comboBox_2.currentText()
        to_port = self.ui.spinBox_2.text()
        
        config.logger.debug(f"add {from_qube}:{from_port} => {to_qube}:{to_port}")
        utils.add_forward_rule(from_qube, int(from_port), to_qube, to_port)
        self.item.done(1)

class Firewall:
    def __init__(self, item: widgets.QDialog):
        self.item = item
        self.ui = pyui.firewall.Ui_Form()
        self.ui.setupUi(self.item)
        
        running = utils.get_qubes_running()
        names = [q.name for q in running]
        
        # show running qubes names
        self.ui.comboBox.clear()
        self.ui.comboBox.addItems(names)

        # connect buttons
        self.ui.cancel.clicked.connect(lambda : self.on_cancel())
        self.ui.add.clicked.connect(self.on_add)

    def on_cancel(self):
        config.logger.debug("firewall cancel")
        self.item.reject()

    def on_add(self):
        qube = self.ui.comboBox.currentText()
        port = self.ui.spinBox.text()
        config.logger.debug(f"firewall open port {qube}:{port}")
        utils.add_firewall_rule(qube, int(port))
        self.item.done(1)