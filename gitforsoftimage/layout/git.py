import os

from PyQt4 import uic, QtGui, QtCore

from wishlib.si import si
from wishlib.qt.QtGui import QDialog
from wishlib.qt.decorators import bussy

from ..gitutils import git, prefs
from .history import History
from .branches import Branches


class Git(QDialog):

    def __init__(self, parent=None):
        super(Git, self).__init__(parent)
        self.repo = si.ActiveProject.Path
        self.prefs = prefs(os.path.join(self.repo, "prefs.json"))
        # init repo
        si.Git_Init()
        # ui stuff
        self.initUI()

    def initUI(self):
        ui_dir = os.path.join(os.path.dirname(__file__), "ui")
        self.ui = uic.loadUi(os.path.join(ui_dir, "git.ui"), self)
        # set icons
        icons = {"branch_button": "iconmonstr-direction-6-icon.png",
                 "history_button": "iconmonstr-time-5-icon.png",
                 "prefs_button": "iconmonstr-wrench-16-icon.png",
                 "sync_button": "iconmonstr-connection-2-ico.png",
                 "reload_button": "iconmonstr-refresh-3-icon.png"}
        for widget, icon_file in icons.iteritems():
            icon_file = os.path.join(ui_dir, "images", icon_file)
            getattr(self.ui, widget).setIcon(QtGui.QIcon(icon_file))
        self.reload_clicked()

    @bussy
    def reload_clicked(self):
        # get branch
        branch = git("branch", cwd=self.repo).stdout
        if len(branch):
            branch = [x[2:]
                      for x in branch.split("\n") if x.startswith("*")][0]
        else:
            branch = "master"
        self.ui.branch_button.setText(branch)
        # reset message
        self.ui.message_lineEdit.setText("")
        # get repository status and list files
        status = git("status", "-s", cwd=self.repo)
        self.ui.files_listWidget.clear()
        for each_file in status.stdout.split("\n"):
            if not len(each_file):
                continue
            item = QtGui.QListWidgetItem(each_file)
            item.setFlags(
                QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
            item.setCheckState(QtCore.Qt.Checked)
            self.ui.files_listWidget.addItem(item)

    def file_clicked(self, item):
        # toggle item state
        toggle = [2, 2, 0]
        item.setCheckState(toggle[int(item.checkState())])

    @bussy
    def commit_clicked(self):
        # check
        message = str(self.ui.message_lineEdit.text())
        cond = [not len(message),
                not bool(self.ui.files_listWidget.count()),
                str(self.ui.branch_button.text()) == "(no branch)"]
        if any(cond):
            self.ui.message_lineEdit.setFocus()
            return
        # get files to add
        to_add = list()
        to_rm = list()
        for i in range(self.ui.files_listWidget.count()):
            item = self.ui.files_listWidget.item(i)
            if item.checkState() == 2:
                name = str(item.text())
                if "D" in name[:3]:
                    to_rm.append(name[3:])
                else:
                    to_add.append(name[3:])
        # add and commit files
        git("rm", "--", *to_rm, cwd=self.repo)
        git("add", "--", *to_add, cwd=self.repo)
        git("commit", "-m", message, cwd=self.repo)
        # reload files
        self.reload_clicked()

    def prefs_clicked(self):
        si.Git_Preferences()

    def branch_clicked(self):
        dialog = Branches(self)
        dialog.ui.branch_label.setText(self.ui.branch_button.text())
        if dialog.exec_():
            self.reload_clicked()

    @bussy
    def history_clicked(self):
        dialog = History(self)
        if dialog.exec_():
            self.reload_clicked()
