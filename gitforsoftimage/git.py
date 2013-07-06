import os
import subprocess
from collections import namedtuple


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
