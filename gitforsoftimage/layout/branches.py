import os

from PyQt4 import uic, QtGui
from wishlib.si import si
from wishlib.qt.QtGui import QDialog

from ..gitutils import git, unlink_file, hard_checkout
from.merge import Merge


class Branches(QDialog):

    def __init__(self, parent=None):
        super(Branches, self).__init__(parent)
        self.repo = si.ActiveProject.Path
        ui_dir = os.path.join(os.path.dirname(__file__), "ui")
        self.ui = uic.loadUi(os.path.join(ui_dir, "branches.ui"), self)
        # set icons
        icons = {"remove_button": "iconmonstr-x-mark-5-icon.png"}
        for widget, icon_file in icons.iteritems():
            icon_file = os.path.join(ui_dir, "images", icon_file)
            getattr(self.ui, widget).setIcon(QtGui.QIcon(icon_file))
        # ui stuff
        self.initUI()

    def initUI(self):
        branches = git("branch", "-a", cwd=self.repo).stdout.split("\n")
        self.branches = [x[2:]
                         for x in branches if not x.startswith("*") and len(x)]
        self.list_branches(self.branches)

    def list_branches(self, branches):
        self.ui.branches_listWidget.clear()
        self.ui.branches_listWidget.addItems(branches)

    def filter_changed(self, text=None):
        text = str(self.ui.filter_lineEdit.text())
        branches = [branch for branch in self.branches if text in branch]
        self.list_branches(branches)

    def branches_changed(self, index):
        enabled = bool(self.ui.branches_listWidget.currentItem())
        self.ui.remove_button.setEnabled(enabled)

    def add_clicked(self):
        branch = str(self.ui.filter_lineEdit.text())
        if not len(branch):
            return
        git("checkout", "-b", branch, cwd=self.repo)
        git("add", ".", cwd=self.repo)
        git("commit", "-m", "new branch: " + branch, cwd=self.repo)
        self.branches.append(branch)
        self.filter_changed()

    def remove_clicked(self):
        branch = str(self.ui.branches_listWidget.currentItem().text())
        result = git("branch", "-d", branch, cwd=self.repo)
        if len(result.stderr):
            ok = QtGui.QMessageBox.warning(self, "Git - Branches",
                                           "The branch '" + branch + "' is not fully merged.\n" +
                                           "Do you want to continue anyway?",
                                           QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel,
                                           QtGui.QMessageBox.Ok)
            if ok == QtGui.QMessageBox.Cancel:
                return
            git("branch", "-D", branch, cwd=self.repo)
        self.branches.remove(branch)
        self.filter_changed()

    def branches_clicked(self, QModelIndex):
        self.accept()

    @unlink_file
    def accept(self):
        item = self.ui.branches_listWidget.currentItem()
        if item:
            branch = str(item.text())
            hard_checkout(branch, self.repo)
        else:
            self.add_clicked()
        super(Branches, self).accept()

    def merge_clicked(self):
        if Merge(self).exec_():
            super(Branches, self).accept()
