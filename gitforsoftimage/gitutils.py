from collections import namedtuple
from functools import wraps
from wishlib.si import si, sianchor
from wishlib.qt.QtGui import QDialog
from PyQt4.QtGui import QMessageBox
import subprocess
import json
import os
import shutil


class prefs(dict):

    """Extend a dictionary to save and load from file"""
    def __init__(self, filepath, *args, **kwds):
        super(prefs, self).__init__(*args, **kwds)
        self.filepath = filepath

    def __setitem__(self, key, value):
        super(prefs, self).__setitem__(key, value)
        # save dict as json file
        with open(self.filepath, "w") as f:
            json.dump(self, f, indent=4)

    def __getitem__(self, key):
        # if there's a file, read it and return data from there
        if os.path.exists(self.filepath):
            with open(self.filepath) as f:
                data = json.load(f)
            value = data.get(key)
            if value:
                return value
        # otherwise just do the usual thing
        else:
            super(prefs, self).__getitem__(key)


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
    # get log and return value
    stdout, stderr = proc.communicate()
    value = proc.wait()
    # return a namedtuple with the results
    results = namedtuple("git_call", "value, stdout, stderr")
    return results._make((value, stdout, stderr))


def unlink_file(function):
    @wraps(function)
    def _decorated(*args, **kwds):
        current_scene = si.ActiveProject.ActiveScene.Filename.Value
        opened = os.path.exists(current_scene)
        if opened:
            si.NewScene("", False)
        f = function(*args, **kwds)
        if opened and os.path.exists(current_scene):
            si.OpenScene(current_scene, False)
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
