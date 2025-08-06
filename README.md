## What's this

Setup script for ARMA 3 server on linux, with workshop mods.

## How to use

- Install Python: `sudo apt install python3`
- Download the project files somewhere (ex: your home folder).

    `git clone https://github.com/jeromehage/arma3-server.git` then `cd arma3-server`.
- Make a Steam account and edit setup.json with the username.
- Edit server.cfg with your server details.
- In the same folder, also add the exported modfile.html you want to use to setup.json.
- Run the first script: `python3 1-setup.py`
- See printed instructions to change user and run: `python3 2-download.py`
- Use the printed command to launch the server. Consider using screen or tmux.
- [optional] add `-port=2402` to the launch command to change ports for multiple servers.

## How to run a custom mission
- Export your mission as multiplayer to `Mission.Name.pbo`.

    (usually in `C:\Program Files (x86)\Steam\steamapps\common\Arma 3\MPMissions\`)
- Copy it to `~/servers/server_name/arma3/mpmissions/Mission.Name.pbo`.
- Edit server.cfg to add it to the mission cycle, autocycle = 1, permanent = 1, voting off.
- Login to the server with the regular password, then type `#login adminpassword` in `/` chat to become admin. Edit difficulty settings and start. You may need to select commander slot.

## Q/A
- Missing .bikeys for some mods:

    Some mods are not signed. If this is not the case, a mod did not download correctly. Try running 2-download.py again, checking for "Success." of steamcmd. If that fails, delete `~/Steam/steamapps` folder and download everything again.
- Mods are not signed by a key accepted by this server:

    Edit server.cfg line `verifySignatures = 0;`.
- Steam query data overflow error:

    Edit server.cfg line `steamProtocolMaxDataSize = 8192;` or a bigger number.
- Server shows, but can't connect, no slots available.

    It could be that you are running two servers on the same ports.
- 

## Source:
- https://community.bistudio.com/wiki/Arma_3:_Dedicated_Server
- https://github.com/fiskce/Arma3-Server-Mod-Manager-Linux/blob/main/armamm.sh
- https://github.com/GameServerManagers/LinuxGSM/blob/master/lgsm/config-default/config-lgsm/arma3server/_default.cfg
- https://www.reddit.com/r/arma/comments/n7mz0e/how_to_get_sog_prairie_fire_dlc_running_on_arma_3/
- https://help.ips-hosting.com/de/article/arma-iii-warning-steam-query-data-overflow-145emxd/

