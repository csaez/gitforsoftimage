import os
from PyQt4 import uic, QtGui, QtCore
from wishlib.qt.QtGui import QDialog
from .. import git


class Commit(QDialog):

    def __init__(self, parent=None):
        super(Commit, self).__init__(parent)
        uifile = os.path.join(os.path.dirname(__file__), "ui", "commit.ui")
        self.ui = uic.loadUi(uifile, self)
        self.COLUMNS = ("Message", "Date", "User", "Hash")
        self.ui.log_tableWidget.setColumnCount(len(self.COLUMNS))
        self.ui.log_tableWidget.setHorizontalHeaderLabels(self.COLUMNS)
        self.check = git.checkgit()

    def set_filepath(self, filepath):
        self.filepath = filepath
        self.reload()  # show history

    def reload(self):
        if not self.check or not len(self.filepath) or not git.tracked(self.filepath):
            return
        logdata = git.git("log", self.filepath)
        for i, data in enumerate(git.logparser(logdata)):
            self.ui.log_tableWidget.insertRow(i)
            for k, v in data.iteritems():
                item = QtGui.QTableWidgetItem()
                item.setFlags(QtCore.Qt.ItemIsEnabled)
                item.setText(v)
                col = [x.lower() for x in self.COLUMNS].index(k)
                self.ui.log_tableWidget.setItem(i, col, item)
        self.ui.log_tableWidget.setCurrentItem(
            self.ui.log_tableWidget.item(0, 0))

    def ok_clicked(self):
        msg = str(self.ui.message_lineEdit.text())
        if len(msg):
            git.git("add", self.filepath)
            git.git("commit", self.filepath, "-m", msg)
            self.close()
        else:
            self.ui.message_lineEdit.setFocus()
