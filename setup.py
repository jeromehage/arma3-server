# source:
# https://community.bistudio.com/wiki/Arma_3:_Dedicated_Server
# https://github.com/fiskce/Arma3-Server-Mod-Manager-Linux/blob/main/armamm.sh
# https://github.com/GameServerManagers/LinuxGSM/blob/master/lgsm/config-default/config-lgsm/arma3server/_default.cfg
# https://www.reddit.com/r/arma/comments/n7mz0e/how_to_get_sog_prairie_fire_dlc_running_on_arma_3/

import os
import subprocess
import pwd

def run(cmd, dry = False, pipe = False, user = None):
    if dry:
        print(cmd)
    else:
        if pipe:
            res = subprocess.run(cmd, stdout = subprocess.PIPE, shell = True, user = user)
            return str(res.stdout.strip())
        else:
            #os.system(cmd)
            subprocess.Popen(cmd, shell = True, user = user).wait()
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
# use a short name without spaces like 'ww2italy'
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
ids = {}
mod_names = {}
if os.path.exists(modfile):
    with open(modfile, 'r') as f:
        raw = f.read()
    for r in raw.split('</tr>')[:-1]:

        # get mod id from the workshop link
        href = r.split('href="')[1].split('"')[0].strip()
        if 'id=' not in href:
            continue
        # between id= and the next parameter
        i = href.find('id=') + 3
        j = href.find(',', i) + 1
        if j == 0:
            j = len(href)
        mod_id = href[i: j]

        # get mod display name
        name = r.split('DisplayName">')[1].split('</td>')[0].strip()

        ids[mod_id] = name

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

# switch to user
current_user = run('whoami', pipe = True)
u = None
if current_user != user:
    # they are all soap to me
    #run('sudo -i -u {}'.format(user))
    #run('sudo -u {} -s'.format(user))
    #run('sudo su {} -'.format(user))
    # run commands as a different user since we are currently logged in as root
    u = user
    # WARNING: os.rename and os.makedirs is still as root
    # need to somehow switch or chown everything
    # TODO: split script into 2 parts, one user one root
    # check https://stackoverflow.com/questions/8025294/changing-user-in-python

# prep folders for installation
os.chdir(home)
for path in [armapath, gamepath, profile1, profile2]:
    if not os.path.exists(path):
        os.makedirs(path, exist_ok = True)

# download steamcmd
os.chdir(home + '/steamcmd')
if not os.path.exists(steamcmd):
    run('wget -c https://steamcdn-a.akamaihd.net/client/installer/steamcmd_linux.tar.gz', user = u)
    run('tar xf steamcmd_linux.tar.gz', user = u)
run(steamcmd + ' +force_install_dir {} +quit'.format(armapath), user = u)

# download or update arma
if update or not os.path.exists('{}/{}'.format(armapath, 'arma3server_x64')):  
    run(steamcmd + ' +login anonymous +app_update 233780 validate +quit', user = u)

# also server DLC pack
if needdlc:
    if update or not os.path.exists('{}/{}'.format(armapath, 'vn')):
        run(steamcmd + ' +login anonymous +app_update 233780 -beta creatordlc validate +quit', user = u)

# link base arma3 installation to server arma3
run('ln -s "{}" "{}"'.format(armapath, gamepath), user = u)
run('chown -R {} {}'.format(user, gamepath), user = u)
# might also need to chmod 777 -R it

# also copy server configuration
run('cp {}/server.cfg {}/server.cfg'.format(cwd, gamepath), user = u)
#run('cp {}/{}.Arma3Profile {}/{}.Arma3Profile'.format(cwd, server, profile2, server), user = u)

# setup mods
# empty /mods and /keys from previous data
run('find {} -type l -exec rm {{}} \;'.format(modspath), user = u)
run('find {} -type l -exec rm {{}} \;'.format(keyspath), user = u)

# download each mod and link it to the arma folder
download = steamcmd + ' +login anonymous +workshop_download_item 107410 {} validate +quit'

unsigned = []
for mod_id in ids:

    path = '{}/{}'.format(workshop, mod_id)
    bikey = False

    # download or update mod
    if update_mods or not os.path.exists(path):

        # delete old workshop folder
        run('rm -rf {}'.format(path), user = u)

        # download again
        run(download.format(mod_id), user = u)
        run('chown -R {} {}'.format(user, path), user = u)

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
    run('ln -s "{}" "{}/{}"'.format(path, modspath, mod_id), user = u)

    # also link .bikeys to our /keys folder
    for root, dirs, files in os.walk(path, topdown = True):
        for f in files:
            if f.endswith('.bikey'):
                run('ln -s "{}" "{}/{}"'.format(os.path.join(root, f), keyspath, f), user = u)
                bikey = True

    # mod is unsigned if no .bikeys are found
    if bikey == False:
        unsigned += [mod_id]

    # find internal mod name
    # like the "@CUP_Vehicles" names in Windows
    # note: not sure if this is useful
    for cfgfile in ['meta.cpp', 'mod.cpp']:
        cfgpath = '{}/{}'.format(path, cfgfile)
        if os.path.exists(cfgpath):
            with open(cfgpath, 'r') as f:
                cfg = f.read()
                for line in cfg.split('\n'):
                    if line.startswith('name = "'):
                        name = line.split('"')[1]
                        mod_names[mod_id] = name
        # stop looking
        if mod_id in mod_names:
            break
                        

## DONE
print('\nREADY! Use the following commands to start the server:\n')
run('cd {}'.format(gamepath), dry = True)

dlcs = ';'.join(dlc)
mods = ';'.join(['mods/{}'.format(i) for i in ids])
cmd = './arma3server_x64 -name={} -config=server.cfg -mod={};{}'.format(server, dlcs, mods)
#cmd = './arma3server_x64 -name={} -profile={} -config=server.cfg -mod={};{}'.format(server, server, dlcs, mods)
run(cmd, dry = True)

print('\nwhich is equivalent to below on Windows\n')
mods = ';'.join(['mods/@{}\\'.format(mod_names.get(i, v)) for i, v in ids.items()])
cmd = './arma3server_x64 -name={} -config=server.cfg -mod="{};{}"'.format(server, dlcs, mods)
run(cmd, dry = True)

print('\nMake sure to update ports in server.cfg for multiple servers.')

if len(unsigned) > 0:
    print('\nWarning: no .bikeys found for these mods:', ', '.join(['{} ({})'.format(ids[i], i) for i in unsigned]))
