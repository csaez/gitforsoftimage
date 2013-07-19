import os
from wishlib.si import log, C, show_qt


def XSILoadPlugin(in_reg):
    in_reg.Author = "csaez"
    in_reg.Name = "GitForSoftimage Plugin"
    in_reg.Major = 1
    in_reg.Minor = 0
    in_reg.RegisterCommand("GitForSoftimage")
    in_reg.RegisterEvent("EndFileExport", C.siOnEndFileExport)
    in_reg.RegisterEvent("EndSceneSave2", C.siOnEndSceneSave2)
    in_reg.RegisterEvent("EndSceneSaveAs", C.siOnEndSceneSaveAs)
    return True


def XSIUnloadPlugin(in_reg):
    log("{} has been unloaded.".format(in_reg.Name), C.siVerbose)
    return True


def GitForSoftimage_Execute():
    from gitforsoftimage.layout.git import Git
    show_qt(Git)


def EndFileExport_OnEvent(in_ctxt):
    log("EndFileExport_OnEvent called", C.siVerbose)
    launcher()
    return False


def EndSceneSave2_OnEvent(in_ctxt):
    log("EndSceneSave2_OnEvent called", C.siVerbose)
    launcher()
    return False


def EndSceneSaveAs_OnEvent(in_ctxt):
    log("EndSceneSaveAs_OnEvent called", C.siVerbose)
    launcher()
    return False


def launcher():
    from gitforsoftimage.gitutils import prefs
    filepath = os.path.join(Application.ActiveProject.Path, "prefs.json")
    if prefs(filepath).get("tracked"):
        Application.GitForSoftimage()
