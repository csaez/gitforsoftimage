import os
import re

from PyQt4 import uic, QtGui
from wishlib.si import si
from wishlib.qt.QtGui import QDialog

from ..gitutils import git, unlink_file, hard_checkout


class Merge(QDialog):

    def __init__(self, parent=None):
        super(Merge, self).__init__(parent)
        self.repo = si.ActiveProject.Path
        ui_dir = os.path.join(os.path.dirname(__file__), "ui")
        self.ui = uic.loadUi(os.path.join(ui_dir, "merge.ui"), self)
        self.initUI()

    def initUI(self):
        branches = git("branch", cwd=self.repo).stdout.split("\n")
        branches = [x[2:] for x in branches if len(x)]
        self.ui.src_comboBox.addItems(branches)
        self.ui.dst_comboBox.addItems(branches)

    @unlink_file
    def accept(self):
        src = str(self.ui.src_comboBox.currentText())
        dst = str(self.ui.dst_comboBox.currentText())
        if dst == src:
            self.ui.src_comboBox.setFocus()
            return
        hard_checkout(dst, self.repo)
        merge = git("merge", src, cwd=self.repo)
        if len(merge.stderr):
            print merge.stderr
            for err in merge.stderr.split("\n"):
                conflict = re.compile("files:\s(.*)\s\(HEAD").findall(err)
                if not len(conflict):
                    continue
                conflict = conflict[0]
                msg = QtGui.QMessageBox.warning(self, "Merge Conflict", err +
                                                "\nDo you want to OVERWRITE " +
                                                dst,
                                                QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel,
                                                QtGui.QMessageBox.Ok)
                if msg == QtGui.QMessageBox.Ok:
                    git("checkout", "--theirs", "--", conflict, cwd=self.repo)
                else:
                    git("checkout", "--ours", "--", conflict, cwd=self.repo)
                git("add", conflict, cwd=self.repo)
            git("commit", "-m", "Merge branch '{}'".format(src), cwd=self.repo)
        super(Merge, self).accept()
