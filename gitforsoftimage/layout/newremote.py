import os

from PyQt4 import uic, QtGui
from wishlib.si import si, OverrideWin32Controls
from wishlib.qt.QtGui import QDialog

from ..gitutils import git


class NewRemote(QDialog):
    ICONS = {"dir_button": "iconmonstr-folder-icon.png"}

    def __init__(self, parent=None):
        super(NewRemote, self).__init__(parent)
        self.repo = si.ActiveProject.Path
        self.setWindowIcon(parent.windowIcon())
        self.initUI()

    def initUI(self):
        ui_dir = os.path.join(os.path.dirname(__file__), "ui")
        self.ui = uic.loadUi(os.path.join(ui_dir, "new_remote.ui"), self)
        for widget, icon_file in self.ICONS.iteritems():
            icon_file = os.path.join(ui_dir, "images", icon_file)
            getattr(self.ui, widget).setIcon(QtGui.QIcon(icon_file))

    def accept(self):
        alias = str(self.ui.alias_lineEdit.text())
        repo_dir = str(self.ui.dir_lineEdit.text())
        if not len(alias) or not len(repo_dir):
            self.ui.alias_lineEdit.setFocus()
            return
        git("remote", "add", alias, repo_dir, cwd=self.repo)
        super(NewRemote, self).accept()

    @OverrideWin32Controls
    def dir_clicked(self):
        repo_dir = QtGui.QFileDialog.getExistingDirectory(
            self, "GitForSoftimage", "/home",
            QtGui.QFileDialog.ShowDirsOnly | QtGui.QFileDialog.DontResolveSymlinks)
        if repo_dir:
            self.ui.dir_lineEdit.setText(repo_dir)
