# This file is part of gitforsoftimage.
# Copyright (C) 2014  Cesar Saez

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation version 3.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import re

from wishlib.si import si
from wishlib.qt import QtGui, loadUi, widgets

from ..gitutils import git, unlink_file, hard_checkout


class Merge(widgets.QDialog):

    def __init__(self, parent=None):
        super(Merge, self).__init__(parent)
        self.repo = si.ActiveProject.Path
        ui_dir = os.path.join(os.path.dirname(__file__), "ui")
        self.ui = loadUi(os.path.join(ui_dir, "merge.ui"), self)
        self.setWindowIcon(parent.windowIcon())
        self.initUI()

    def initUI(self):
        branches = git("branch", "-a", cwd=self.repo).stdout.split("\n")
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
                msg = QtGui.QMessageBox.warning(
                    self, "Merge Conflict", err +
                    "\nDo you want to OVERWRITE " + dst,
                    QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel,
                    QtGui.QMessageBox.Ok)
                if msg == QtGui.QMessageBox.Ok:
                    git("checkout", "--theirs", "--", conflict, cwd=self.repo)
                else:
                    git("checkout", "--ours", "--", conflict, cwd=self.repo)
                git("add", conflict, cwd=self.repo)
            git("commit", "-m", "Merge branch '{}'".format(src), cwd=self.repo)
        super(Merge, self).accept()
