import os
import json
from utilities import run

## READ CONFIG FILE
with open('setup.json', 'r') as f:
    config = json.load(f)

# set to True to download arma3 again (and dlcs if needed)
# will create server folders and symlink arma3 in both cases
update = config['update']

# set to True to download workshop mods again
# will empty mods and keys folders then symlink the right ones in both caes
update_mods = config['update_mods']

# the exported list of mods
modfile = config['modfile']

# dlcs to use
# ex: set to [] for vanilla, SOG is ['vn']
dlc = config['dlc']

# you do not need to own ARMA to download "ARMA 3 Linux dedicated server"
# but it is recommended that you make a different steam account for steamcmd
steam_account = config['steam_account']

# also recommended to run steamcmd and arma3 under a different linux user
user = config['user']

# multiple server configuration
# uses /arma3 as a base and symlinks to it
# use a short name without spaces like 'ww2italy'
server = config['server']


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

# you need to run the script as the arma user
# otherwise os.rename and os.makedirs will belong to root
current_user = run('whoami', pipe = True)
if current_user != user:
    raise AssertionError(
        'Expected {} user, currently {}, . Make sure to run 1-setup.py first!'.format(
            current_user, user
            )
        )

# read the list of mod IDs from the modfile
# if the modfile does not exist, do not use mods
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

needdlc = len(dlc) > 0
needmod = len(ids) > 0

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
run(steamcmd + ' +force_install_dir {} +quit'.format(armapath))

# download or update arma
if update or not os.path.exists('{}/{}'.format(armapath, 'arma3server_x64')):  
    run(steamcmd + ' +login anonymous +app_update 233780 validate +quit')

# also server DLC pack
if needdlc:
    dlcs_installed = [os.path.exists('{}/{}'.format(armapath, d)) for d in dlc]
    if update or not all(dlcs_installed):
        run(steamcmd + ' +login anonymous +app_update 233780 -beta creatordlc validate +quit')

# link base arma3 installation to server arma3
run('ln -s "{}" "{}"'.format(armapath, gamepath))
run('chown -R {} {}'.format(user, gamepath))
# might also need to chmod 777 -R it

# also copy server configuration
run('cp {}/server.cfg {}/server.cfg'.format(cwd, gamepath))
#run('cp {}/{}.Arma3Profile {}/{}.Arma3Profile'.format(cwd, server, profile2, server))

# setup workshop mods
# empty /mods and /keys from previous data
run('find {} -type l -exec rm {{}} \;'.format(modspath))
run('find {} -type l -exec rm {{}} \;'.format(keyspath))

# download each mod and link it to the arma folder
download = steamcmd + ' +login anonymous +workshop_download_item 107410 {} validate +quit'

unsigned = []
for mod_id in ids:

    path = '{}/{}'.format(workshop, mod_id)
    bikey = False

    # download or update mod
    if update_mods or not os.path.exists(path):

        # delete old workshop folder
        run('rm -rf {}'.format(path))

        # download again
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

print('cd {}'.format(gamepath))

launch = './arma3server_x64 -name={server} -config=server.cfg'
#launch = './arma3server_x64 -name={server} -profile={server} -config=server.cfg'
dlcs = ';'.join(dlc)
mods = ';'.join(['mods/{}'.format(i) for i in ids])
cmd = launch.format(server = server)
if needdlc or needmod:
    cmd += ' -mod=' + ';'.join([s for s in [dlcs, mods] if s != ''])
print(cmd)

print('\nwhich is equivalent to below on Windows\n')
mods = ';'.join(['mods/@{}\\'.format(mod_names.get(i, v)) for i, v in ids.items()])
cmd = launch.format(server = server)
if needdlc or needmod:
    cmd += ' -mod=' + ';'.join([s for s in [dlcs, mods] if s != ''])
print(cmd)

print('\nMake sure to update ports in server.cfg for multiple servers.')

if len(unsigned) > 0:
    print('\nWarning: no .bikeys found for these mods:', ', '.join(['{} ({})'.format(ids[i], i) for i in unsigned]))
