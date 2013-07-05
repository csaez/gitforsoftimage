import os
import re
import json
import shutil
from collections import namedtuple

from PyQt4.QtGui import QMessageBox
from wishlib.si import sianchor
from wishlib.qt.QtGui import QDialog

from ..git import git
from .layout.gitdialog import GitDialog


class Manager(object):

    def __init__(self, repo_dir):
        super(Manager, self).__init__()
        self.repo = repo_dir
        # ensure git is working
        if self.tracked and len(git("status", cwd=self.repo).stderr):
            self.git_init()

    def git_init(self):
        # create a wishlib dialog as parent to preserve style
        anchor = QDialog(sianchor())
        msg = "Do you want to create a local repository for this project?"
        dialog = QMessageBox.question(anchor, "GitForSoftimage", msg,
                                      QMessageBox.Yes | QMessageBox.No,
                                      QMessageBox.No)
        anchor.close()  # close parent
        if dialog == QMessageBox.Yes:
            git("init", cwd=self.repo)
            shutil.copy(os.path.join(os.path.dirname(__file__), "data",
                                     ".gitignore"), self.repo)
            return
        self.tracked = False

    @property
    def tracked(self):
        return self.prefs.get("tracked")

    @tracked.setter
    def tracked(self, value):
        self.prefs["tracked"] = value
        self.prefs = self.prefs.copy()  # save on disk
        if value and len(git("status", cwd=self.repo).stderr):
            self.git_init()

    @property
    def prefs(self):
        if hasattr(self, "_prefs"):
            return self._prefs
        filepath = os.path.join(self.repo, "prefs.json")
        if os.path.exists(filepath):
            with open(filepath) as f:
                self._prefs = json.load(f)
        else:
            self._prefs = {"tracked": True}
            with open(filepath, "w") as f:
                json.dump(self._prefs, f)
        return self._prefs

    @prefs.setter
    def prefs(self, value):
        self._prefs = value
        with open(os.path.join(self.repo, "prefs.json"), "w") as f:
            json.dump(self._prefs, f)

    def commit_file(self, filepath):
        if not self.tracked or self.repo not in filepath:
            return
        fileinfo = self.get_fileinfo(filepath)
        value, message = GitDialog.commit(sianchor(), fileinfo)
        if value:
            git("add", filepath, cwd=self.repo)
            git("commit", filepath, "-m", message, cwd=self.repo)
        return value

    def checkout_file(self, filepath):
        cond = (self.repo in filepath, self.tracked,
                "??" not in git("status", filepath, "-s").stdout)
        if not all(cond):
            return
        fileinfo = self.get_fileinfo(filepath)
        value, commit = GitDialog.checkout(sianchor(), fileinfo)
        if value:
            git("checkout", commit.branch)
            git("checkout", commit.commit, "--", filepath)
        return value

    def get_fileinfo(self, filepath):
        """
        Returns a sorted list (active branch first) with git info about the file.

        Ussage:
        for info in get_fileinfo(filepath):
            print "branch:", info.branch
            for commit in info.history:
                print commit.commit
                print commit.author
                print commit.date
                print commit.message
                print " "
        """
        commit_info = namedtuple("commit_info",
                                 "commit, author, date, message")
        branch_info = namedtuple("branch_info", "branch, history")
        results = list()
        # get branches
        branch_log = git("branch", cwd=self.repo).stdout
        branches = re.compile("^(.*)\n", re.MULTILINE).findall(branch_log)
        # sort branches (active as the first one) and remove first chars
        branches = [i[2:] for i in sorted(branches,
                                          key=lambda x: not x.startswith("*"))]
        for branch in branches:
            git("checkout", branch, cwd=self.repo)
            # get file history
            logs = git("log", filepath)
            regex = "commit\s(.{40})\nAuthor:\s*(.*)\nDate:\s*(.*)\s{6}(.*)"
            commits = re.compile(regex, re.MULTILINE).findall(logs.stdout)
            info = (branch, [commit_info._make(i) for i in commits])
            results.append(branch_info._make(info))
        # swith back to original branch
        git("checkout", results[0].branch, cwd=self.repo)
        return results
