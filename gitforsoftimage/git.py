import subprocess
import os
import re


def git(*args, **kwds):
    #check git version
    if not checkgit():
        return
    # if there is not a explicit cwd look get it from a filepath on args
    if not kwds.get("cwd"):
        for i in args:
            if not os.path.exists(i):
                continue
            kwds["cwd"] = os.path.dirname(i)
    # set and execute the git subprocess
    cmd = ["git"]
    cmd.extend(args)
    kwds["stdout"] = subprocess.PIPE
    kwds["stderr"] = subprocess.PIPE
    kwds["shell"] = True  # skip shell window
    proc = subprocess.Popen(cmd, **kwds)
    stdout_str, stderr_str = proc.communicate()
    proc.wait()
    if len(stderr_str):
        raise Exception(stderr_str)
    return stdout_str


def logparser(log):
    # regex
    messages = re.compile("\s{6}(.*)").findall(log)
    users = re.compile("Author:\s*(.*)").findall(log)
    dates = re.compile("Date:\s*(.*)").findall(log)
    hashes = re.compile("commit\s(.{40})").findall(log)
    for i in range(len(hashes)):
        yield {"hash": hashes[i], "date": dates[i],
               "message": messages[i], "user": users[i]}


def tracked(filepath):
    try:
        # ?? indicate a not tracked file
        if "??" not in git("status", filepath, "-s"):
            return True
    except:
        # if there is no repo at filepath git will fail
        pass
    return False


def checkgit():
    try:
        if subprocess.call("git --version", shell="True") == 0:
            return True
    except:
        pass
    print("ERROR: git doesnt found")
    return False
