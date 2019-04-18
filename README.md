# pve-changedomain
Mass-Update the search domain for LXC containers in a Proxmox cluster

## Installation:
- Download proxmoxer (`pip3 install proxmoxer --user`)
- Clone this repository (or download the script directly: `https://raw.githubusercontent.com/AriosThePhoenix/pve-changedomain/master/changedomain.py`)
- Adjust the variables at the top of `changedomain.py` (olddomain, newdomain, and pve host vars)
- Run: `./changedomain.py`

## Warning
changedomain.py will have to shutdown the containers to change the domain. Any container that was shut down will be restarted automatically, unless an error occurs, in which case the container will remain stopped to avoid inconsistency errors.
