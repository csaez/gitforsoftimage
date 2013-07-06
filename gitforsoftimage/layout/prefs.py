import os

from wishlib.si import si
from wishlib.qt.QtGui import QDialog
from PyQt4 import uic

from ..manager import Manager
from ..git import git


class Prefs(QDialog):

    def __init__(self, parent=None):
        super(Prefs, self).__init__(parent)
        self.manager = Manager(si.ActiveProject.Path)
        self.MAPPING = {"tracked": "tracked",
                        "commit": "commit_onsave",
                        "checkout": "checkout_onload",
                        "dependencies": "dependencies"}
        self.initUI()

    def initUI(self):
        uifile = os.path.join(os.path.dirname(__file__), "ui", "prefs.ui")
        self.ui = uic.loadUi(uifile, self)
        # project settings
        self.ui.project_lineEdit.setText(self.manager.repo)
        for k, v in self.MAPPING.iteritems():
            item = getattr(self.ui, k + "_checkBox")
            pref = self.manager.prefs.get(v)
            item.setChecked(bool(pref))
            func = (lambda x=k: self.checkbox_clicked(x))
            item.pressed.connect(func)
        # git config
        config = lambda x: git("config", "--global", x)
        self.ui.user_lineEdit.setText(config("user.name").stdout[:-1])
        self.ui.user_lineEdit.editingFinished.connect(self.user_changed)
        self.ui.email_lineEdit.setText(config("user.email").stdout[:-1])
        self.ui.email_lineEdit.editingFinished.connect(self.email_changed)
        self.git_status()
        self.tracked_clicked()

    # SLOTS
    def checkbox_clicked(self, widget_name):
        pref_name = self.MAPPING.get(widget_name)
        widget = getattr(self.ui, widget_name + "_checkBox")
        self.manager.prefs[pref_name] = not widget.isChecked()
        print pref_name, not widget.isChecked()

    def user_changed(self):
        git("config", "--global", "user.name",
            str(self.ui.user_lineEdit.text()))
        self.git_status()

    def email_changed(self):
        git("config", "--global", "user.email",
            str(self.ui.email_lineEdit.text()))
        self.git_status()

    def git_status(self):
        status = git("version", cwd=self.manager.repo).stdout
        self.ui.status_label.setText("Status:\n" + status)

    def tracked_clicked(self):
        value = self.ui.tracked_checkBox.isChecked()
        self.ui.commit_checkBox.setEnabled(value)
        self.ui.checkout_checkBox.setEnabled(value)
        self.ui.dependencies_checkBox.setEnabled(value)
        self.ui.deleterepo_button.setEnabled(not value)
        if value and len(git("status", cwd=self.manager.repo).stderr):
            self.manager.git_init(False)
