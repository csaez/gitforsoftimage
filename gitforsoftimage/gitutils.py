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
import shutil
import subprocess
from collections import namedtuple
from functools import wraps

from wishlib.utils import JSONDict
from wishlib.qt import QtGui, widgets
from wishlib.si import si, sianchor


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
        anchor = widgets.QDialog(sianchor())
        ok = QtGui.QMessageBox.warning(
            anchor, "Discard changes",
            "Your local changes would be overwritten.\n" +
            "Do you want to continue?",
            QtGui.QMessageBox.Ok | QtGui.QMessageBox.Cancel,
            QtGui.QMessageBox.Ok)
        anchor.close()
        if ok == QtGui.QMessageBox.Cancel:
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
            JSONDict(os.path.join(repo, "prefs.json"))["tracked"]]
    if all(cond):
        shutil.copy(os.path.join(data_dir, ".gitignore"), repo)
        git("init", cwd=repo)
        git("checkout", "-b", "master", cwd=repo)
