# Lab 1 - Creating Your First Network

## Adding an Authgroup

### Overview
We are going add a real (lab) device to NSO, but first we will be adding a netsim device to NSO, and then pull the configs from both device. Netsim is a virtual device used for local testing, generated from a NSO NED, initiated through a Bash NSO command.

Finally we will add both devices to a device-group (a logical grouping of devices, which may or may not have the same authgroups).

### Creating an Authgroup
**First** we need to create an 'authgroup', which is basically equivalent to our Cisco PGM.

Log into NSO CLI and type this command, given your proper credentials (first enter configure mode):
```
ncs_cli -C -u admin
conf
devices authgroups group myauthgroup default-map remote-name USER remote-password PASS remote-secondary-password ENABLEPASS
admin@ncs(config-group-default)# commit
Commit complete.
```
*The above command is saying that for the parent command, working with our devices, let's create an authgroup for those devices (aka PGM) called default.*

*Then, for that new authgroup let's add a login name named 'admin'. The remote-secondary-password is the enable password it will try if needed.*

In a **typical NSO situation on your own**, you would add your .web password for the remote-password part, and the PGM NOC enable password for the remote-secondary-password part.

Thus we have a new authgroup with a login username, default password and a backup enable password.

## Running NSO with a real Cisco Device

Now that we have credentials set up, we need to tell NSO which device we want to add by either specifying the IP.

NSO needs a couple of things to make changes to a network device:
- **Device info** (a name to call it-typically the hostname, an IP address, the type of NED to be used, an authgroup-basically the same as a PGM, ssh keys and network connectivity)
-An **authgroup**, which is basically a PGM group (username, password, enable password). You can have multiple authgroups, and each device must associated with an authgroup.
-The device needs to be **admin state unlocked**. By default when a device is added to the NSO list of devices, it is in admin state locked. In order to initiate a sync-from to pull the config (or to do any configuration change), the device must be first unlocked. It is best to lock the devices again after finishing, to avoid any accidental configuration.
-NSO needs to know what type of device it is interacting with (IOS, IOS-XR, NX-OS, etc). This is called the **NED (Network Element Driver)**.
- NSO needs to pull the **SSH keys** from the device. This is done only after the commit has occured and the device
- Finally you need to tell it to grab a local copy of the **device's running config**. NSO calls this process "sync-from," where NSO logs into the device and captures the running-config to parse it into NSO's local XML database. This local copy of the config will only be updated upon a request of sync-from. It does not automatically update. You can do a 'check-sync' to quickly find out if the NSO local config version is the same as the one currently on the device. We will cover this shortly.


Here are the commands in NSO to add a new device with the device name first, then saying what the IP address is, and what authgroup we are using for it. We then specify that the device is a cli based device, and that cli style device is using the cisco-ios NED. Finally we unlock it so that we can sync-from the config into the NSO database. We then commit these changes. Unless they are commited, nothing has occured. It is like 'write mem' more or less.

I am using svl290-gg04-asr1004-wan-gw3 device for example, but please use your own below, use the -econ ending for the ssh address, NSO will do the DNS lookup:
```
admin@ncs(config-group-myauthgroup)# top
admin@ncs(config)# devices device svl290-gg04-asr1004-wan-gw3 address svl290-gg04-asr1004-wan-gw3-econ authgroup myauthgroup
admin@ncs(config-device-svl290-gg04-asr1004-wan-gw3)# device-type cli ned-id cisco-ios
admin@ncs(config-device-svl290-gg04-asr1004-wan-gw3)# state admin-state unlocked
admin@ncs(config-device-svl290-gg04-asr1004-wan-gw3)# commit
```

Now the the device basic info is in NSO and commited (if you did not commit, it will not be able to sync-from yet), we will get the ssh keys from the device to verify the identity, and do an initial sync-from:
```
admin@ncs(config-device-svl290-gg04-asr1004-wan-gw3)# ssh fetch-host-keys
result updated
fingerprint {
    algorithm ssh-rsa
    value X
}
admin@ncs(config-device-svl290-gg04-asr1004-wan-gw3)# sync-from
result true
admin@ncs(config-device-svl290-gg04-asr1004-wan-gw3)# end
admin@ncs#
```


## Running NSO with a Netsim IOS device

### Creating an NSO Virtual device (in linux, not inside NSO)

Going outside of the NSO application, back into the linux bash CLI, let's create a few netsim devices (back into Linux bash shell CLI).

type exit to get back to the bash cli
```
exit
```

Now I am creating a netsim device in a directory (with a prefix for the virtual devices of idoNetsim, using the cisco-ios NED package full path), and then starting those virtual devices (ncs-netsim start):

Netsim devices are a quick and easy way to test configuration changes with no risk.

#### Look at the options for the  ncs-netsim bash command
```
ncs-netsim --help
```

We are going to create one netsim device using the cisco-ios NED as the image type. Create and start a device with the Bash commands below.

```
ncs-netsim create-device cisco-ios mydevice
cd netsim
ncs-netsim start
ncs-netsim is-alive
```
You can use ncs-netsim is-alive to see if it is currently online. It is not necessary to use that command in the creation process.

You have to change into the directory of where the netsim device is created to start it.

### Adding the netsim device to NSO


Adding a netsim device into NSO application

You get the port information with this command (assuming you have some netsim devices created):
ncs-netsim list

ncs-netsim list output for the above netsim device example:
```
[root@svl-sjc-nso-1 ~]# ncs-netsim list
ncs-netsim list for  /root/netsim

name=mydevice netconf=12022 snmp=11022 ipc=5010 cli=10022 dir=/root/netsim/mydevice/mydevice
[root@svl-sjc-nso-1 ~]#
```


I get the port info for the CLI to plug into my NSO, along with the hostname: 10022 (cli=10022).

You can log into one of the netsim devices like this (if you want to see the config and play around):
```
ncs-netsim cli-c mydevice
```

Now let's, log back into NSO :
```
ncs_cli -C -u admin
```
 and add a netsim device from earlier:
 ```
config
devices device mydevice
address 127.0.0.1 port 10022
device-type cli ned-id cisco-ios protocol ssh
authgroup default
state admin-state unlocked
commit
ssh fetch-host-keys
sync-from
end
```


### Creating a Device Group

We are going to create a device-group called NSO_TEST :
```
config
devices device-group NSO_TEST
device-name [ mydevice svl290-gg04-asr1004-wan-gw3 ]
commit
 ```

 The syntax to add devices to a device group (and other lists of things in NSO is as follows):
 command [ entry1 entry2 etc ]


# Now You Try:
 1. Create a netsim network of 2 devices, add them to NSO and and your other lab device to NSO
 2. Add those three new devices to your NSO
 3. Create a new device group just for your netsim devices
