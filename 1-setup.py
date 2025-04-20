import os
import json
from utilities import run, user_exists, package_is_installed

## READ CONFIG FILE
with open('setup.json', 'r') as f:
    config = json.load(f)

# it is recommended to run steamcmd and arma3 under a different linux user
user = config['user']

# dirs
cwd = os.getcwd()
home = '/home/' + user

## SETUP

# download required packages
for pkg in ['wget', 'lib32gcc-s1']:
    if not package_is_installed(pkg):
        run('sudo apt install ' + pkg)
        if not package_is_installed(pkg):
            raise RuntimeError('Could not install: {}'.format(pkg))

# create user
if not user_exists(user):
    run('sudo useradd -m -s /bin/bash {}'.format(user))

if not os.path.exists(home):
    os.makedirs(home, exist_ok = True)
    run('chown -R {} {}'.format(user, home))

## DONE
print('STEP 1 DONE. Use the following commands to continue:\n')
print('sudo su {} -'.format(user))
print('cd {}'.format(cwd))
print('python3 2-download.py')

# they are all soap to me
#print('sudo -i -u {}'.format(user))
#print('sudo -u {} -s'.format(user))
#print('sudo su {} -'.format(user))
