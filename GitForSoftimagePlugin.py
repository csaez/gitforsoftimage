from wishlib.si import si, log, C, show_qt


def XSILoadPlugin(in_reg):
    in_reg.Author = "csaez"
    in_reg.Name = "GitForSoftimage Plugin"
    in_reg.Major = 1
    in_reg.Minor = 0
    in_reg.RegisterCommand("Git Preferences", "Git_Preferences")
    in_reg.RegisterCommand("Git Commit Scene", "Git_Commit_Scene")
    in_reg.RegisterCommand("Git Checkout Scene", "Git_Checkout_Scene")
    in_reg.RegisterEvent("BeginFileImport", C.siOnBeginFileImport)
    in_reg.RegisterEvent("BeginSceneOpen", C.siOnBeginSceneOpen)
    in_reg.RegisterEvent("EndFileExport", C.siOnEndFileExport)
    in_reg.RegisterEvent("EndSceneSave2", C.siOnEndSceneSave2)
    in_reg.RegisterEvent("EndSceneSaveAs", C.siOnEndSceneSaveAs)
    return True


def XSIUnloadPlugin(in_reg):
    log("{} has been unloaded.".format(in_reg.Name), C.siVerbose)
    return True


def GitPreferences_Execute():
    from gitforsoftimage.layout.prefs import Prefs
    show_qt(Prefs)


def GitCommitScene_Execute():
    from gitforsoftimage.manager import Manager
    manager = Manager(si.ActiveProject.Path)
    value = manager.prefs.get("commit_onsave")
    manager.prefs["commit_onsave"] = True
    si.SaveScene()
    manager.prefs["commit_onsave"] = value


def GitCheckoutScene_Execute():
    from gitforsoftimage.manager import Manager
    manager = Manager(si.ActiveProject.Path)
    value = manager.prefs.get("checkout_onload")
    manager.prefs["checkout_onload"] = True
    si.OpenScene()
    manager.prefs["checkout_onload"] = value


def BeginFileImport_OnEvent(in_ctxt):
    log("BeginFileImport_OnEvent called", C.siVerbose)
    from gitforsoftimage.manager import Manager
    manager = Manager(si.ActiveProject.Path)
    if not manager.prefs.get("checkout_onload"):
        return False
    filepath = str(in_ctxt.GetAttribute("FileName"))
    manager.checkout_file(filepath)
    return False


def BeginSceneOpen_OnEvent(in_ctxt):
    log("BeginSceneOpen_OnEvent called", C.siVerbose)
    from gitforsoftimage.manager import Manager
    manager = Manager(si.ActiveProject.Path)
    if not manager.prefs.get("checkout_onload"):
        return False
    filepath = str(in_ctxt.GetAttribute("FileName"))
    if filepath == str(si.ActiveProject.ActiveScene.FileName.Value):
        # create new scene to unlock the actual one
        si.NewScene("", False)
    manager.checkout_file(filepath)
    return False


def EndFileExport_OnEvent(in_ctxt):
    log("EndFileExport_OnEvent called", C.siVerbose)
    from gitforsoftimage.manager import Manager
    manager = Manager(si.ActiveProject.Path)
    if not manager.prefs.get("commit_onsave"):
        return False
    filepath = str(in_ctxt.GetAttribute("FileName"))
    manager.commit_file(filepath)
    return False


def EndSceneSave2_OnEvent(in_ctxt):
    log("EndSceneSave2_OnEvent called", C.siVerbose)
    from gitforsoftimage.manager import Manager
    manager = Manager(si.ActiveProject.Path)
    if not manager.prefs.get("commit_onsave"):
        return False
    filepath = str(in_ctxt.GetAttribute("FileName"))
    manager.commit_file(filepath)
    return False


def EndSceneSaveAs_OnEvent(in_ctxt):
    log("EndSceneSaveAs_OnEvent called", C.siVerbose)
    from gitforsoftimage.manager import Manager
    manager = Manager(si.ActiveProject.Path)
    if not manager.prefs.get("commit_onsave"):
        return False
    filepath = str(in_ctxt.GetAttribute("FileName"))
    manager.commit_file(filepath)
    return False
