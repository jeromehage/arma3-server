## What's this

Setup script for ARMA 3 server on linux, with workshop mods.

## How to use

- Install Python: `sudo apt install python3`
- Download the project files somewhere (ex: your home folder).
   
    `git clone https://github.com/jeromehage/arma3-server.git` then `cd arma3-server`.
- Make a Steam account and edit setup.json with the username.
- Edit server.cfg with your server details.
- In the same folder, also add the exported modfile.html you want to use.
- Run the first script: `python3 1-setup.py`
- Follow the steps to run the second script.
- Follow the steps to launch the server.
- [optional] Change ports for multiple servers on the same machine.

## Source:
- https://community.bistudio.com/wiki/Arma_3:_Dedicated_Server
- https://github.com/fiskce/Arma3-Server-Mod-Manager-Linux/blob/main/armamm.sh
- https://github.com/GameServerManagers/LinuxGSM/blob/master/lgsm/config-default/config-lgsm/arma3server/_default.cfg
- https://www.reddit.com/r/arma/comments/n7mz0e/how_to_get_sog_prairie_fire_dlc_running_on_arma_3/
- https://help.ips-hosting.com/de/article/arma-iii-warning-steam-query-data-overflow-145emxd/
