# Configuring Device ios config, making static templates and Device Groups
## Introduction

In this lab we are going to:
1. Configure the config of a device and a device-group using CLI Commands
2. Create a static template (no variables)
3. Apply the template to a device group



## Configuring devices

Log into NSO, and enter config mode if not already. Make sure your devices are state admin-state unlocked. Pick a device and enter into that device tree like below and check out the config options for that device. Configure an interface description

-Note, depending on your test device, you may have to adapt your interface name from GigabitEthernet 0/0/0 to whatever is a real interface on that device

```
** go into configure mode**
conf

admin@ncs(config)# devices device svl290-gg04-asr1004-wan-gw3
admin@ncs(config-device-svl290-gg04-asr1004-wan-gw3)# config
admin@ncs(config-config)# ios:interface GigabitEthernet ?
This line doesn't have a valid range expression
Possible completions:
  <0-66>/<0-128>   GigabitEthernet interface number
  0
  0/0/0
  0/0/1
  0/2/0
  0/2/1
  ---
  range
admin@ncs(config-config)# ios:interface GigabitEthernet 0/0/0 ?
Possible completions: (first 100)
access-session           Access Session specific Interface Configuration Commands
 arp                      Set arp type (arpa, probe, snap), timeout, log options orpacket priority
 authentication           set the port-control value
 auto                     Configure Automation
 ....
 admin@ncs(config-config)# ios:interface GigabitEthernet 0/0/0
admin@ncs(config-if)# description NSO Training
```

#### Now we will take a look and see what commands NSO will send, outformating the change into native which is standard Cisco CLI syntax.

```
admin@ncs(config-if)# commit dry-run outformat ?
Possible completions:
  cli  native  xml
  admin@ncs(config-if)# commit dry-run outformat native
  native {
      device {
          name test1
          data interface GigabitEthernet0/0/0
                description NSO Training
               exit
      }
  }
  admin@ncs(config-if)#
```
## Now You Try

1. Change the interface description for a range of interfaces on your test device.
2. Explore the different '|' and '?' options, try saving the config change output to a file and try adding multiple '|' options, using 'details' and 'debug xpath' options.

## Device Templates

The power of NSO is configuration compliance and building service models (especially ones which include templates). Let's create our first template.

### Creating the config template

The device template is in config mode, under the devices tree. The text below creates a template with the name defined in quotes.

```
admin@ncs(config)# devices template "My First Template"
admin@ncs(config-template-My First Template)#
 ```

### Adding configuration to the config template
Now we need to say what configuration is going to be applied to the template

Cisco IOS related configuration by using the ‘ios:’ tag (since NSO covers many variants of CLIs, IOS, IOS XE, NX OS, Arista, etc., we need to tell NSO which variation of CLI- the NED, to choose)
See some of the options for various NEDs (ios, ios-xr, nx-os)

Now choosing the ios:lldp command option:

```
admin@ncs(config-template-My First Template)# config
admin@ncs(config-config)# ios:lldp run
admin@ncs(config-config)# commit dry-run
....
admin@ncs(config-config)# commit
Commit complete.
admin@ncs(config-config)#
admin@ncs(config-config)# top
admin@ncs(config)#
 ```


### Applying the template to a device group

Now we can apply the template to this device group:
```
admin@ncs(config)# devices device-group NSO_TEST
admin@ncs(config-device-group-NSO_TEST)#
admin@ncs(config-device-group-NSO_TEST)# apply-template template-name ?
Possible completions:
  My First Template
admin@ncs(config-device-group-NSO_TEST)# apply-template template-name My\ First\ Template
apply-template-result {
    device mydevice
    result ok
}
apply-template-result {
    device test1
    result ok
}
admin@ncs(config-device-group-NSO_TEST)# commit dry-run outformat native
native {
    device {
        name mydevice
        data lldp run
    }
    device {
        name test1
        data lldp run
    }
}
admin@ncs(config-device-group-NSO_TEST)#
 ```

The commit dry-run will show you what commands are going to be sent. I chose outformat native, to show it in Cisco-CLI data format.
Now, you need to commit it.
 ```
admin@ncs(config)# commit
Commit complete.
admin@ncs(config)# exit
admin@ncs#
```

You can also include variables in the templates, which if you look at the '?' options when you apply the template, gives options for input on the variables.

Now You try:
1. Create a template with some configuration you want, try to enforce it on a device and a device group
2. Try rolling back configuration through the GUI (Views Rollback dropdown) and/or the CLI (it is under config->rollback)
3. Create  a template with one or many variables (see slides for examples)
