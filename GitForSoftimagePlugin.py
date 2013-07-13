from wishlib.si import log, C, show_qt


def XSILoadPlugin(in_reg):
    in_reg.Author = "csaez"
    in_reg.Name = "GitForSoftimage Plugin"
    in_reg.Major = 1
    in_reg.Minor = 0
    in_reg.RegisterCommand("GitForSoftimage")
    return True


def XSIUnloadPlugin(in_reg):
    log("{} has been unloaded.".format(in_reg.Name), C.siVerbose)
    return True


def GitForSoftimage_Execute():
    from gitforsoftimage.layout.git import Git
    show_qt(Git)
