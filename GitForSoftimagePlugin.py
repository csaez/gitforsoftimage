import os
import shutil
from wishlib.si import si, log, C, show_qt


def XSILoadPlugin(in_reg):
    in_reg.Author = "csaez"
    in_reg.Name = "GitForSoftimage Plugin"
    in_reg.Major = 1
    in_reg.Minor = 0
    in_reg.RegisterCommand("Git")
    in_reg.RegisterCommand("Git Init", "Git_Init")
    in_reg.RegisterCommand("Git Preferences", "Git_Preferences")
    return True


def XSIUnloadPlugin(in_reg):
    log("{} has been unloaded.".format(in_reg.Name), C.siVerbose)
    return True


def Git_Execute():
    from gitforsoftimage.layout.git import Git
    show_qt(Git)


def GitPreferences_Execute():
    from gitforsoftimage.layout.prefs import Prefs
    show_qt(Prefs)


def GitInit_Execute():
    from gitforsoftimage.gitutils import git
    repo = si.ActiveProject.Path
    if len(git("status", cwd=repo).stderr):
        # init a new repo
        data_dir = os.path.join(os.path.dirname(git.__file__), "data")
        shutil.copy(os.path.join(data_dir, ".gitignore"), repo)
        shutil.copy(os.path.join(data_dir, "prefs.json"), repo)
        git("init", cwd=repo)
