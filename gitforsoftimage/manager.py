import os
import re
import json
import shutil
from collections import namedtuple

from PyQt4.QtGui import QMessageBox
from wishlib.si import sianchor, si
from wishlib.qt.QtGui import QDialog

from .git import git
from .layout.gitdialog import GitDialog


class Prefs(dict):

    def __init__(self, filepath, *args, **kwds):
        super(Prefs, self).__init__(*args, **kwds)
        self.filepath = filepath

    def __setitem__(self, key, value):
        super(Prefs, self).__setitem__(key, value)
        with open(self.filepath, "w") as f:
            json.dump(self, f, indent=4)


class Manager(object):

    def __init__(self, repo_dir):
        super(Manager, self).__init__()
        self.repo = repo_dir
        # ensure git is working
        if self.prefs.get("tracked") and len(git("status", cwd=self.repo).stderr):
            self.git_init(True)

    def git_init(self, ask=False):
        if ask:
            # create a wishlib dialog as parent to preserve style
            anchor = QDialog(sianchor())
            msg = "Do you want to create a local repository for this project?"
            dialog = QMessageBox.question(anchor, "GitForSoftimage", msg,
                                          QMessageBox.Yes | QMessageBox.No,
                                          QMessageBox.Yes)
            anchor.close()  # close parent
            if dialog == QMessageBox.No:
                self.prefs["tracked"] = False
                return
        git("init", cwd=self.repo)
        shutil.copy(os.path.join(os.path.dirname(__file__), "data",
                                 ".gitignore"), self.repo)
        self.prefs["tracked"] = True

    @property
    def prefs(self):
        if hasattr(self, "_prefs"):
            return self._prefs
        filepath = os.path.join(self.repo, "prefs.json")
        if not os.path.exists(filepath):
            shutil.copy(os.path.join(os.path.dirname(__file__), "data",
                                     "prefs.json"), self.repo)
        with open(filepath) as f:
            self._prefs = json.load(f)
        self._prefs = Prefs(filepath, self._prefs)
        return self._prefs

    def commit_file(self, filepath):
        if not self.prefs["tracked"] or self.repo not in filepath:
            return
        fileinfo = self.get_fileinfo(filepath)
        external_files = list()
        # if we are on the scnene grab external files
        cond = (
            str(filepath) == str(si.ActiveProject.ActiveScene.FileName.Value),
            self.prefs.get("dependencies"))
        if all(cond):
            for path in si.ActiveProject.ActiveScene.ExternalFiles:
                path = str(path.ResolvedPath)
                cond = (self.repo in path, os.path.exists(path),
                        len(git("status", path, "-s").stdout))
                if all(cond):
                    external_files.append(path)
        value, data = GitDialog.commit(sianchor(), fileinfo,
                                       dependencies=external_files)
        if value:
            git("add", filepath, *data.dependencies, cwd=self.repo)
            git("commit", "-m", data.message, cwd=self.repo)
        return value

    def checkout_file(self, filepath):
        cond = (self.repo in filepath, self.prefs["tracked"],
                "??" not in git("status", filepath, "-s").stdout)
        if not all(cond):
            return False
        fileinfo = self.get_fileinfo(filepath)
        # if there's only one commit then select it
        if len(fileinfo[0].history) == 1:
            value, commit = True, (fileinfo[0].history[0].commit,
                                   fileinfo[0].branch)
            commit = namedtuple("commit_info", "commit, branch")._make(commit)
        else:
            value, commit = GitDialog.checkout(sianchor(), fileinfo)
        if value:
            git("checkout", commit.branch)
            git("reset", "--soft", commit.commit)
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
