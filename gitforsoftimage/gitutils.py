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
import json
import shutil
import subprocess
from collections import namedtuple
from functools import wraps

from wishlib.si import si, sianchor
from wishlib.qt.QtGui import QDialog
from PyQt4.QtGui import QMessageBox


class prefs(dict):

    """Extend a dict to save and load from a json file"""

    def __init__(self, fp, *args, **kwds):
        super(prefs, self).__init__(*args, **kwds)
        self.fp = fp
        # init data from file
        if os.path.exists(self.fp):
            with open(self.fp) as fp:
                data = json.load(fp)
            for k, v in data.iteritems():
                self.__setitem__(k, v)

    def __setitem__(self, key, value):
        super(prefs, self).__setitem__(key, value)
        self.__updatejson__()

    def __delitem__(self, key):
        super(prefs, self).__delitem__(key)
        self.__updatejson__()

    def clear(self):
        super(prefs, self).clear()
        self.__updatejson__()

    def update(self, other):
        super(prefs, self).update(other)
        self.__updatejson__()

    def __updatejson__(self):
        with open(self.fp, "w") as fp:
            json.dump(self, fp, indent=4)


def git(*args, **kwds):
    # get command args
    cmd = ["git"]
    cmd.extend(list(args))
    # if there's not an explicit cwd, look for a filepath on the args
    if not kwds.get("cwd"):
        for filepath in args:
            if not os.path.exists(filepath):
                continue
            # set current working directory
            kwds["cwd"] = os.path.dirname(filepath)
    # set subprocess
    kwds["stdout"] = subprocess.PIPE
    kwds["stderr"] = subprocess.PIPE
    kwds["shell"] = True  # hide shell
    proc = subprocess.Popen(cmd, **kwds)
    stdout, stderr = proc.communicate()
    # return results._make((value, stdout, stderr))
    results = namedtuple("git_call", "stdout, stderr")
    return results._make((stdout, stderr))


def unlink_file(function):
    @wraps(function)
    def _decorated(*args, **kwds):
        current_scene = si.ActiveProject.ActiveScene.Filename.Value
        opened = os.path.exists(current_scene)
        if opened:
            si.NewScene("", False)
        f = function(*args, **kwds)
        return f
    return _decorated


def hard_checkout(commit, repo):
    if len(git("status", "-s", cwd=repo).stdout):
        anchor = QDialog(sianchor())
        ok = QMessageBox.warning(anchor, "Discard changes",
                                 "Your local changes would be overwritten.\n" +
                                 "Do you want to continue?",
                                 QMessageBox.Ok | QMessageBox.Cancel,
                                 QMessageBox.Ok)
        anchor.close()
        if ok == QMessageBox.Cancel:
            return
    git("reset", "--hard", cwd=repo)
    git("checkout", commit, cwd=repo)
    git("reset", "--hard", cwd=repo)


def git_init(repo):
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    # copy prefs.json file
    if not os.path.exists(os.path.join(repo, "prefs.json")):
        shutil.copy(os.path.join(data_dir, "prefs.json"), repo)
    # if repo should be tracked init it
    cond = [len(git("status", cwd=repo).stderr),
            prefs(os.path.join(repo, "prefs.json"))["tracked"]]
    if all(cond):
        shutil.copy(os.path.join(data_dir, ".gitignore"), repo)
        git("init", cwd=repo)
        git("checkout", "-b", "master", cwd=repo)
