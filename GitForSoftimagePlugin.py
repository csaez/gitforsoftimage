from wishlib.si import si, log, C, show_qt, sianchor
from wishlib.qt.QtGui import QDialog

from PyQt4.QtGui import QMessageBox
from gitforsoftimage import git
from gitforsoftimage.layout.checkout import Checkout
from gitforsoftimage.layout.commit import Commit


def XSILoadPlugin(in_reg):
    in_reg.Author = "csaez"
    in_reg.Name = "GitForSoftimage Plugin"
    in_reg.Major = 1
    in_reg.Minor = 0
    in_reg.RegisterEvent("BeginFileImport", C.siOnBeginFileImport)
    in_reg.RegisterEvent("BeginSceneOpen", C.siOnBeginSceneOpen)
    in_reg.RegisterEvent("EndFileExport", C.siOnEndFileExport)
    in_reg.RegisterEvent("EndSceneSave2", C.siOnEndSceneSave2)
    in_reg.RegisterEvent("EndSceneSaveAs", C.siOnEndSceneSaveAs)
    return True


def XSIUnloadPlugin(in_reg):
    log("{} has been unloaded.".format(in_reg.Name), C.siVerbose)
    return True


def BeginFileImport_OnEvent(in_ctxt):
    log("BeginFileImport_OnEvent called", C.siVerbose)
    filepath = str(in_ctxt.GetAttribute("FileName"))
    if not git.tracked(filepath):
        # filepath is not tracked, continue normally
        return False
    show_qt(Checkout, modal=True,
            onshow_event=lambda x: x.ui.file_lineEdit.setText(filepath))
    return False


def BeginSceneOpen_OnEvent(in_ctxt):
    log("BeginSceneOpen_OnEvent called", C.siVerbose)
    filepath = str(in_ctxt.GetAttribute("FileName"))
    if not git.tracked(filepath):
        # filepath is not tracked, continue normally
        return False
    if filepath == str(si.ActiveProject.ActiveScene.FileName.Value):
        # create new scene to unlock the actual one
        si.NewScene("", False)
    show_qt(Checkout, modal=True,
            onshow_event=lambda x: x.set_filepath(filepath))
    return False


def EndFileExport_OnEvent(in_ctxt):
    log("EndFileExport_OnEvent called", C.siVerbose)
    commit(str(in_ctxt.GetAttribute("FileName")))
    return False


def EndSceneSave2_OnEvent(in_ctxt):
    log("EndSceneSave2_OnEvent called", C.siVerbose)
    commit(str(in_ctxt.GetAttribute("FileName")))
    return False


def EndSceneSaveAs_OnEvent(in_ctxt):
    log("EndSceneSaveAs_OnEvent called", C.siVerbose)
    commit(str(in_ctxt.GetAttribute("FileName")))
    return False


def commit(filepath):
    try:
        status = git.git("status", filepath, "-s")
    except:
        # if there is not repo at filepath git will fail
        status = ""
        if init_repo():
            status = git.git("status", filepath, "-s")
    if len(status):
        show_qt(Commit, modal=True,
                onshow_event=lambda x: x.set_filepath(filepath))


def init_repo():
    anchor = QDialog(sianchor())
    msg = "Do you want to create a local repository for this project?"
    dialog = QMessageBox.question(anchor, "GitForSoftimage", msg,
                                  QMessageBox.Yes | QMessageBox.No,
                                  QMessageBox.No)
    anchor.close()
    if dialog == QMessageBox.Yes:
        # init repo
        git.git("init", cwd=si.ActiveProject.Path)
        return True
    return False
