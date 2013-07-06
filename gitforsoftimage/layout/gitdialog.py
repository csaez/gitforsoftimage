import os
from collections import namedtuple
from PyQt4 import uic, QtGui, QtCore
from wishlib.qt.QtGui import QDialog


class GitDialog(QDialog):

    @classmethod
    def commit(cls, parent, info, dependencies=[]):
        dialog = cls(parent, info, commit=True, dependencies=dependencies)
        dialog.data = str()
        result = dialog.exec_()
        return result, dialog.data

    @classmethod
    def checkout(cls, parent, info):
        dialog = cls(parent, info, commit=False)
        dialog.data = str()
        result = dialog.exec_()
        return result, dialog.data

    def __init__(self, parent, fileinfo, commit=True, dependencies=[]):
        super(GitDialog, self).__init__(parent)
        self.fileinfo = fileinfo
        self.commit = commit
        self.dependencies = dependencies
        self.initUI()

    def initUI(self):
        file_dir = os.path.dirname(__file__)
        uifile = os.path.join(file_dir, "ui", "gitdialog.ui")
        self.ui = uic.loadUi(uifile, self)
        # set icons
        icon = os.path.join(file_dir, "ui", "images", "branch_icon&32.png")
        self.ui.branch_button.setIcon(QtGui.QIcon(icon))
        # set history headers
        self.COLS = ("Message", "Date", "User", "Commit")
        self.ui.history_tableWidget.setColumnCount(len(self.COLS))
        self.ui.history_tableWidget.setHorizontalHeaderLabels(self.COLS)
        # add branches
        self.ui.branch_comboBox.addItems([i.branch for i in self.fileinfo])
        # set visibility
        self.ui.message_lineEdit.setVisible(self.commit)
        self.ui.dependencies_groupBox.setVisible(self.commit)
        self.ui.history_groupBox.setChecked(not self.commit)
        banner_text = ("Git - checkout ", "Git - commit ")[int(self.commit)]
        self.ui.banner_label.setText(banner_text)
        if self.commit:
            self.dependencies_reload()
            self.ui.message_lineEdit.setFocus()
        else:
            self.ui.history_tableWidget.setFocus()

    def history_reload(self):
        # clear table
        for i in range(self.ui.history_tableWidget.rowCount()):
            self.ui.history_tableWidget.removeRow(0)
        branch_name = str(self.ui.branch_comboBox.currentText())
        history = [
            i.history for i in self.fileinfo if i.branch == branch_name][0]
        # fill table
        for i, commit in enumerate(history):
            self.ui.history_tableWidget.insertRow(i)
            for j, value in enumerate(commit):
                item = QtGui.QTableWidgetItem()
                item.setFlags(
                    QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                item.setText(value)
                self.ui.history_tableWidget.setItem(i, 3 - j, item)
        # select the first row
        self.ui.history_tableWidget.setCurrentItem(
            self.ui.history_tableWidget.item(0, 0))

    def dependencies_reload(self):
        if not len(self.dependencies):
            self.ui.dependencies_groupBox.setChecked(False)
        # clear table
        for i in range(self.ui.dependencies_tableWidget.rowCount()):
            self.ui.dependencies_tableWidget.removeRow(0)
        # fill table
        for i, value in enumerate(self.dependencies):
            self.ui.dependencies_tableWidget.insertRow(i)
            item = QtGui.QTableWidgetItem()
            item.setFlags(
                QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
            item.setText(value)
            item.setCheckState(QtCore.Qt.Checked)
            self.ui.dependencies_tableWidget.setItem(i, 0, item)
        # select the first row
        self.ui.dependencies_tableWidget.setCurrentItem(
            self.ui.dependencies_tableWidget.item(0, 0))

    def dependencies_clicked(self, x, y):
        states = [2, 0, 0]
        item = self.ui.dependencies_tableWidget.item(x, y)
        item.setCheckState(states[item.checkState()])

    def ok_clicked(self):
        if self.commit:
            dependencies = list()
            if self.ui.dependencies_groupBox.isChecked():
                for i in range(self.ui.dependencies_tableWidget.rowCount()):
                    item = self.ui.dependencies_tableWidget.item(i, 0)
                    if item.checkState():
                        dependencies.append(str(item.text()))
            data = namedtuple("data_info", "message, dependencies")
            self.data = data._make((str(self.ui.message_lineEdit.text()),
                                   dependencies))
        else:
            index = self.ui.history_tableWidget.currentRow()
            commit = str(self.ui.history_tableWidget.item(index, 3).text())
            data = namedtuple("commit_info", "commit, branch")
            branch = str(self.ui.branch_comboBox.currentText())
            self.data = data._make((commit, branch))
        if self.commit and not len(self.data.message):
            print "Please enter a commit message"
            self.ui.message_lineEdit.setFocus()
            return
        self.accept()

    def history_clicked(self, index):
        if not self.commit:
            self.ok_clicked()

    def history_toggled(self, value):
        height = (20, 16777215)[int(value)]
        self.ui.history_groupBox.setMaximumHeight(height)

    def dependencies_toggled(self, value):
        height = (20, 16777215)[int(value)]
        self.ui.dependencies_groupBox.setMaximumHeight(height)

    def branch_changed(self, branch_name):
        self.history_reload()

    def branch_clicked(self):
        pass
