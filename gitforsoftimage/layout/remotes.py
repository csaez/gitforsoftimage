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

from wishlib.si import si
from wishlib.qt import QtGui, loadUi, widgets

from ..gitutils import git
from .newremote import NewRemote


class Remotes(widgets.QDialog):
    ICONS = {"reload_button": "iconmonstr-refresh-3-icon.png",
             "add_button": "iconmonstr-plus-icon.png",
             "remove_button": "iconmonstr-minus-icon-256.png"}

    def __init__(self, parent=None):
        super(Remotes, self).__init__(parent)
        self.repo = si.ActiveProject.Path
        self.initUI()

    def initUI(self):
        ui_dir = os.path.join(os.path.dirname(__file__), "ui")
        self.ui = loadUi(os.path.join(ui_dir, "remotes.ui"), self)
        for widget, icon_file in self.ICONS.iteritems():
            icon_file = os.path.join(ui_dir, "images", icon_file)
            getattr(self.ui, widget).setIcon(QtGui.QIcon(icon_file))
        self.reload_clicked()

    def reload_clicked(self):
        remotes = git("remote", cwd=self.repo)
        remotes = [x for x in remotes.stdout.split("\n") if len(x)]
        self.ui.remotes_listWidget.clear()
        self.ui.remotes_listWidget.addItems(remotes)
        self.remotes_clicked()

    def add_clicked(self):
        NewRemote(self).exec_()
        self.reload_clicked()

    def remotes_clicked(self, item=None):
        state = self.ui.remotes_listWidget.currentItem() is not None
        self.ui.fetch_button.setEnabled(state)
        self.ui.push_button.setEnabled(state)

    def remove_clicked(self):
        item = self.ui.remotes_listWidget.currentItem()
        if item:
            git("remote", "rm", str(item.text()), cwd=self.repo)
            self.reload_clicked()

    def fetch_clicked(self):
        alias = str(self.ui.remotes_listWidget.currentItem().text())
        fetch = git("fetch", alias, cwd=self.repo)
        if fetch.stderr:
            QtGui.QMessageBox.information(self, "GitForSoftimage",
                                          fetch.stderr)
        self.accept()

    def push_clicked(self):
        alias = str(self.ui.remotes_listWidget.currentItem().text())
        branch = git("branch", cwd=self.repo).stdout.split("\n")
        branch = [x[2:] for x in branch if x.startswith("*")][0]
        push = git("push", alias, branch, cwd=self.repo)
        if push.stderr:
            QtGui.QMessageBox.information(self, "GitForSoftimage",
                                          push.stderr)
        self.accept()
