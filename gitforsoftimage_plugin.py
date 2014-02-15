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
from wishlib.si import si, log, C, show_qt
from wishlib.utils import JSONDict


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
    launcher("commit_onsave")
    return False


def EndSceneSave2_OnEvent(in_ctxt):
    log("EndSceneSave2_OnEvent called", C.siVerbose)
    launcher("commit_onsave")
    return False


def EndSceneSaveAs_OnEvent(in_ctxt):
    log("EndSceneSaveAs_OnEvent called", C.siVerbose)
    launcher("commit_onsave")
    return False


def launcher(param):
    filepath = os.path.join(si.ActiveProject.Path, "prefs.json")
    if not os.path.exists(filepath):
        return
    user_prefs = JSONDict(filepath)
    if user_prefs.get("tracked") and user_prefs.get(param):
        si.GitForSoftimage()
