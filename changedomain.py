#!/usr/bin/env python3

# Author: u/AriosThePhoenix
# Date: 2019-04-18
# License: MIT
# URL: https://github.com/AriosThePhoenix/pve-changedomain

# Mass-Update the search domain for LXC containers in a Proxmox cluster
# Installation:
#   - Download proxmoxer (pip3 install proxmoxer --user)
#   - Adjust the variables below
#   - Run
#
# WARNING: changedomain.py will have to shutdown the containers to change
# the domain. Any container that was shut down will be restarted automatically,
# unless an error occurs, in which case the container will remain stopped to avoid
# inconsistency errors

# The domain to replace
# If you want to replace all undefined domains instead set this to "None"
olddomain = "olddomain.com"
# The new domain that should replace the old domain
newdomain = "newdomain.com"
# Information on a valid Proxmox node.
host = "node1.pve.yourdomain.com"
user = "root@pam"
password = "hunter2"


# --- BEGIN CODE ---

import json
import proxmoxer
import time

pve = proxmoxer.ProxmoxAPI(host, user=user,
                           password=password, verify_ssl=False)
resources = pve.cluster.resources.get()

print("Gettings list of all containers...")
cts = []
for resource in resources:
    if resource["type"] == "lxc":
        ct = {
            "vmid": resource["vmid"],
            "name": resource["name"],
            "node": resource["node"],
            "olddomain": "",
        }
        cts.append(ct)

print("Creating list of containers that need to be updated...")
cts_to_update = []
for ct in cts:
    try:
        ct["olddomain"] = pve.nodes(ct["node"]).lxc(
            ct["vmid"]).config.get()["searchdomain"]
    except KeyError:
        ct["olddomain"] = "None"

    if ct["olddomain"] == olddomain:
        cts_to_update.append(ct)
print("Need to update", len(cts_to_update), "containers")

for ct in cts_to_update:
    print("Changing domain on container", ct["name"], "(vmid=" + str(ct["vmid"]) +  ")...")
    newargs = {"searchdomain": newdomain}

    if pve.nodes(ct["node"]).lxc(ct["vmid"]).status.current.get()["status"] != "stopped":
        print("Shutting down container...")
        try:
            pve.nodes(ct["node"]).lxc(ct["vmid"]).status.shutdown.post()
            while pve.nodes(ct["node"]).lxc(ct["vmid"]).status.current.get()["status"] != "stopped":
                time.sleep(2)

            print("Changing domain...")
            pve.nodes(ct["node"]).lxc(ct["vmid"]).config.put(**newargs)
            print("Restarting container...")
            pve.nodes(ct["node"]).lxc(ct["vmid"]).status.start.post()
        except proxmoxer.ResourceException as e:
            print("ERROR: Could not shutdown container", ct["name"], ". Message:", e)
    else:
        try:
            print("Changing domain...")
            pve.nodes(ct["node"]).lxc(ct["vmid"]).config.put(**newargs)
        except proxmoxer.ResourceException as e:
            print("ERROR: Could not shutdown container", ct["name"], ". Message:", e)

    print("Done\n")
