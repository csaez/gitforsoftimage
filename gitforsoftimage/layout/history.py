import os
import re

from PyQt4 import uic, QtGui
from wishlib.si import si
from wishlib.qt.QtGui import QDialog

from ..gitutils import git, unlink_file, hard_checkout


class History(QDialog):

    def __init__(self, parent=None):
        super(History, self).__init__(parent)
        self.repo = si.ActiveProject.Path
        ui_dir = os.path.join(os.path.dirname(__file__), "ui")
        self.ui = uic.loadUi(os.path.join(ui_dir, "history.ui"), self)
        self.initUI()

    def initUI(self):
        branch = git("branch", cwd=self.repo).stdout
        branch = [x[2:] for x in branch.split("\n") if x.startswith("*")][0]
        log = git("log", branch, cwd=self.repo).stdout
        pattern = "commit\s(.*)\n(?:Merge:.*\n)?Author:\s(.*)\nDate:\s*(.*)\n\s{5}(.*)\n"
        self.history = re.compile(pattern, re.MULTILINE).findall(log)
        for commit, author, date, message in self.history:
            message_item = QtGui.QTreeWidgetItem()
            message_item.setText(0, message)
            message_item.setText(1, date)
            message_item.setText(2, author)
            self.ui.history_treeWidget.addTopLevelItem(message_item)
            # show files per commit
            # files = git("show", "--name-only", commit, cwd=self.repo).stdout
            # files = [i for i in files.split("\n")[6:] if len(i)]
            # for i in files:
            #     file_item = QtGui.QTreeWidgetItem()
            #     file_item.setText(0, i)
            #     message_item.addChild(file_item)

    @unlink_file
    def accept(self):
        item = self.history_treeWidget.currentItem()
        index = self.ui.history_treeWidget.indexOfTopLevelItem(item)
        commit = self.history[index][0]
        hard_checkout(commit, self.repo)
        super(History, self).accept()
