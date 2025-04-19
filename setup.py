# source:
# https://community.bistudio.com/wiki/Arma_3:_Dedicated_Server
# https://github.com/fiskce/Arma3-Server-Mod-Manager-Linux/blob/main/armamm.sh
# https://github.com/GameServerManagers/LinuxGSM/blob/master/lgsm/config-default/config-lgsm/arma3server/_default.cfg
# https://www.reddit.com/r/arma/comments/n7mz0e/how_to_get_sog_prairie_fire_dlc_running_on_arma_3/

import os
import subprocess
#import pwd

def run(cmd, dry = True, pipe = False):
    if dry:
        print(cmd)
    else:
        if pipe:
            res = subprocess.run(cmd, stdout = subprocess.PIPE, shell = True)
            return res.stdout.strip()
        else:
            #os.system(cmd)
            subprocess.Popen(cmd, shell = True).wait()
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

## CONFIG

update = True
update_mods = True

# the exported list of mods
modfile = 'soggy18.04.25.html'

# dlcs to use
# set to [] for vanilla
# ex: SOG is ['vn']
dlc = ['vn']

# you do not need to own ARMA to download "ARMA 3 Linux dedicated server"
# but it is recommended that you make a different steam account for steamcmd
steam_account = 'anonymous'

# also recommended to run steamcmd and arma3 under a different linux user
user = 'arma'

# multiple server configuration
# uses /arma3 as a base and symlinks to it
# use a short name without spaces like 'ww2ita'
server = 'soggy'

# dirs
cwd = os.getcwd()
home = '/home/' + user

workshop = home + '/Steam/steamapps/workshop/content/107410'
steamcmd = home + '/steamcmd/steamcmd.sh'
armapath = home + '/steamcmd/arma3'
profile1 = home + '/.local/share/Arma 3'
profile2 = home + '/.local/share/Arma 3 - Other Profiles'
gamepath = home + '/servers/' + server
modspath = gamepath + '/mods'
keyspath = gamepath + '/keys'


## SETUP
needdlc = len(dlc) > 0

# read the list of mod IDs from the modfile
raw = ''
with open(modfile, 'r') as f:
    raw = f.read()
ids = [i.split('<')[0].split('"')[0].strip() for i in raw.split('?id=')[1:]]
ids = list(set(ids))

# download required packages
for pkg in ['wget', 'lib32gcc-s1']:
    if package_is_installed(pkg):
        run('sudo apt install ' + pkg)
        if not package_is_installed(pkg):
            raise RuntimeError('Could not install: {}'.format(pkg))

# create user
if not user_exists(user):
    run('sudo useradd -m -s /bin/bash {}'.format(user))

if not os.path.exists(home):
    os.makedirs(home, exist_ok = True)

# switch to user
current_user = run('whoami', pipe = True)
if current_user != user:
    # they are all soap to me
    #run('sudo -i -u {}'.format(user))
    #run('sudo -u {} -s'.format(user))
    #run('sudo su {} -'.format(user))
    run('sudo su {} -'.format(user))

# prep folders for installation
os.chdir(home)
for path in [armapath, gamepath, profile1, profile2]:
    if not os.path.exists(path):
        os.makedirs(path, exist_ok = True)

# download steamcmd
os.chdir(home + '/steamcmd')
if not os.path.exists(steamcmd):
    run('wget -c https://steamcdn-a.akamaihd.net/client/installer/steamcmd_linux.tar.gz')
    run('tar xf steamcmd_linux.tar.gz')

# download or update arma
if update or not os.path.exists('{}/{}'.format(armapath, 'arma3server_x64')):
    run(steamcmd + ' +force_install_dir {} +quit'.format(armapath))
    run(steamcmd + ' +login anonymous +app_update 233780 validate +quit')

# also server DLC pack
if needdlc:
    if update or not os.path.exists('{}/{}'.format(armapath, 'vn')):
        run(steamcmd + ' +force_install_dir {} +quit'.format(armapath))
        run(steamcmd + ' +login anonymous +app_update 233780 -beta creatordlc validate +quit')

if update:
    run('ln -s "{}" "{}"'.format(armapath, gamepath))
    run('chown -R {} {}'.format(user, gamepath))

# empty /mods and /keys from previous data
run('find {} -type l -exec rm {{}} \;'.format(modspath))
run('find {} -type l -exec rm {{}} \;'.format(keyspath))

# download each mod and link it to the arma folder
download = steamcmd + ' +login anonymous +workshop_download_item 107410 {} validate +quit'

for mod_id in ids:

    path = '{}/{}'.format(workshop, mod_id)

    # download or update mod
    if update_mods or not os.path.exists(path):
        run(download.format(mod_id))
        run('chown -R {} {}'.format(user, path))

        # make all filenames lowercase
        for root, dirs, files in os.walk(path, topdown = True):
            # with topdown = True, you can make edits to the iterator
            for i, d in enumerate(dirs):
                if d != d.lower():
                    os.rename(os.path.join(root, d), os.path.join(root, d.lower()))
                    dirs[i] = d.lower()
            for i, f in enumerate(files):
                if f != f.lower():
                    os.rename(os.path.join(root, f), os.path.join(root, f.lower()))
                    files[i] = f.lower()

    # link mod to our /mods folder
    run('ln -s "{}" "{}/{}"'.format(path, modspath, mod_id))

    # also link .bikeys to our /keys folder
    for root, dirs, files in os.walk(path, topdown = True):
        for f in files:
            if f.endswith('.bikey'):
                run('ln -s "{}" "{}/{}"'.format(os.path.join(root, f), keyspath, f))

# copy server configuration
run('cp {}/server.cfg {}/server.cfg'.format(cwd, gamepath))
#run('cp {}/{}.Arma3Profile {}/{}.Arma3Profile'.format(cwd, server, profile2, server))

## DONE
print('\nREADY! Use the following commands to start the server:\n')
run('cd {}'.format(gamepath), dry = True)

dlcs = ';'.join(dlc)
mods = ';'.join(['mods/{}'.format(i) for i in ids])
cmd = './arma3server_x64 -name={} -config=server.cfg -mod={};{}'.format(server, dlcs, mods)
#cmd = './arma3server_x64 -name={} -profile={} -config=server.cfg -mod={};{}'.format(server, server, dlcs, mods)
run(cmd, dry = True)

print('\nMake sure to update ports for multiple servers.')
