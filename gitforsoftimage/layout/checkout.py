import os
from PyQt4 import uic, QtGui, QtCore
from wishlib.qt.QtGui import QDialog
from .. import git


class Checkout(QDialog):

    def __init__(self, parent=None):
        super(Checkout, self).__init__(parent)
        uifile = os.path.join(os.path.dirname(__file__), "ui", "checkout.ui")
        self.ui = uic.loadUi(uifile, self)
        self.filepath = ""
        self.COLUMNS = ("Message", "Date", "User", "Hash")
        self.ui.log_tableWidget.setColumnCount(len(self.COLUMNS))
        self.ui.log_tableWidget.setHorizontalHeaderLabels(self.COLUMNS)

    def set_filepath(self, filepath):
        self.filepath = filepath
        self.reload()

    def reload(self):
        if not git.checkgit() or not len(self.filepath) or not git.tracked(self.filepath):
            return
        logdata = git.git("log", self.filepath)
        for i, data in enumerate(git.logparser(logdata)):
            self.ui.log_tableWidget.insertRow(i)
            for k, v in data.iteritems():
                item = QtGui.QTableWidgetItem()
                item.setFlags(
                    QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
                item.setText(v)
                col = [x.lower() for x in self.COLUMNS].index(k)
                self.ui.log_tableWidget.setItem(i, col, item)
        self.ui.log_tableWidget.setCurrentItem(
            self.ui.log_tableWidget.item(0, 0))

    def ok_clicked(self):
        if self.ui.log_tableWidget.rowCount():
            index = self.ui.log_tableWidget.currentRow()
            item = self.ui.log_tableWidget.item(index,
                                                self.COLUMNS.index("Hash"))
            git.git("checkout", str(item.text()), "--", self.filepath)
        self.close()

    def log_clicked(self, index):
        self.ok_clicked()
