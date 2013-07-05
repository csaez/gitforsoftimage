from wishlib.si import si, log, C


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
    from gitforsoftimage.manager import Manager
    filepath = str(in_ctxt.GetAttribute("FileName"))
    Manager(si.ActiveProject.Path).checkout_file(filepath)
    return False


def BeginSceneOpen_OnEvent(in_ctxt):
    log("BeginSceneOpen_OnEvent called", C.siVerbose)
    from gitforsoftimage.manager import Manager
    filepath = str(in_ctxt.GetAttribute("FileName"))
    print si.ActiveProject.Path
    if filepath == str(si.ActiveProject.ActiveScene.FileName.Value):
        # create new scene to unlock the actual one
        si.NewScene("", False)
    Manager(si.ActiveProject.Path).checkout_file(filepath)
    return False


def EndFileExport_OnEvent(in_ctxt):
    log("EndFileExport_OnEvent called", C.siVerbose)
    filepath = str(in_ctxt.GetAttribute("FileName"))
    from gitforsoftimage.manager import Manager
    Manager(si.ActiveProject.Path).commit_file(filepath)
    return False


def EndSceneSave2_OnEvent(in_ctxt):
    log("EndSceneSave2_OnEvent called", C.siVerbose)
    filepath = str(in_ctxt.GetAttribute("FileName"))
    from gitforsoftimage.manager import Manager
    Manager(si.ActiveProject.Path).commit_file(filepath)
    return False


def EndSceneSaveAs_OnEvent(in_ctxt):
    log("EndSceneSaveAs_OnEvent called", C.siVerbose)
    filepath = str(in_ctxt.GetAttribute("FileName"))
    from gitforsoftimage.manager import Manager
    Manager(si.ActiveProject.Path).commit_file(filepath)
    return False
