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
from wishlib.qt.QtGui import QDialog
from PyQt4 import uic

from ..gitutils import git, prefs, git_init


class Prefs(QDialog):

    def __init__(self, parent=None):
        super(Prefs, self).__init__(parent)
        self.repo = si.ActiveProject.Path
        self.prefs = prefs(os.path.join(self.repo, "prefs.json"))
        self.initUI()

    def initUI(self):
        uifile = os.path.join(os.path.dirname(__file__), "ui", "prefs.ui")
        self.ui = uic.loadUi(uifile, self)
        # project settings
        self.ui.project_lineEdit.setText(self.repo)
        self.ui.tracked_checkBox.setChecked(bool(self.prefs["tracked"]))
        self.ui.commit_checkBox.setChecked(bool(self.prefs["commit_onsave"]))
        # git config
        config = lambda x: git("config", "--global", x)
        self.ui.user_lineEdit.setText(config("user.name").stdout[:-1])
        self.ui.user_lineEdit.editingFinished.connect(self.user_changed)
        self.ui.email_lineEdit.setText(config("user.email").stdout[:-1])
        self.ui.email_lineEdit.editingFinished.connect(self.email_changed)
        self.git_status()
        self.tracked_clicked()

    # SLOTS
    def user_changed(self):
        git("config", "--global", "user.name",
            str(self.ui.user_lineEdit.text()))
        self.git_status()

    def email_changed(self):
        git("config", "--global", "user.email",
            str(self.ui.email_lineEdit.text()))
        self.git_status()

    def git_status(self):
        status = git("version", cwd=self.repo).stdout
        self.ui.status_label.setText("Status:\n" + status)

    def tracked_clicked(self):
        value = self.ui.tracked_checkBox.isChecked()
        self.prefs["tracked"] = value
        self.ui.commit_checkBox.setEnabled(value)
        if value:
            git_init(self.repo)

    def commit_clicked(self):
        self.prefs["commit_onsave"] = self.ui.commit_checkBox.isChecked()

    def ignore_clicked(self):
        os.startfile(os.path.join(self.repo, ".gitignore"))
