import subprocess
import pwd

def run(cmd, pipe = False, user = None):
    # subprocess.run to always wait
    if pipe:
        res = subprocess.run(cmd, stdout = subprocess.PIPE, shell = True, user = user)
        out = res.stdout.decode('utf-8').strip()
        return out
    else:
        subprocess.run(cmd, shell = True, user = user)
        return

def user_exists(usr):
    try:
        pwd.getpwnam(usr)
        return True
    except KeyError:
        return False

def package_is_installed(pkg):
    res = run("dpkg-query -W -f='${Status}\\n' " + pkg, pipe = True)
    return 'installed' in res
