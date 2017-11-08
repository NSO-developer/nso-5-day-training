# Day 2 Lab 2 - Using NSO for Show Commands

In this lab we will be reinforcing the concepts of interacting with network devices using NSO. NSO can send immediate commands to devices, which can be useful to gather the current state of the network.

One thing to note, NSO does not store the show command data into it's database, so it only is gathered for your information. Later on if you are using the python interactions with the NSO config database, it can be helpful to use the show commands to gather data to make decisions for your python logic.

# Prepping the Syntax

The NSO CLI syntax is a bit odd to send the command, so you will likely need to reference this in the future, as it can be hard to remember.

```
admin@ncs# devices device lab-gw0 live-status exec ?
Possible completions:
  any          Execute any command on device
  clear        Reset functions
  copy         Copy from one file to another
  license      Smart licensing Commands
  ping         Send echo messages
  reload       Halt and perform a cold restart
  show         Execute show commands
  traceroute   Trace route to destination
  verify       Verify a file
admin@ncs#
```
There are multiple live-status command tree options to choose, the easiest one is "any" because you can send any command to the device. The other ones may be useful in specific contexts.

Here for example is a show command using the "any" command.

Here I issue a show run to the netsim, note that I used " " to surround the command:
```
admin@ncs# devices device lab-gw0 live-status exec any "show run"
result
tailfned police cirmode
no service password-encryption
aaa accounting delay-start
no cable admission-control preempt priority-voice
no cable qos permission create
no cable qos permission update
no cable qos permission modems
ip source-route
no ip gratuitous-arps
no ip cef
ip finger
no ip http server
no ip http secure-server
no ip forward-protocol nd
ipv6 unicast-routing
no ipv6 cef
no dot11 syslog
interface Loopback0
 no shutdown
 ip address 127.0.0.1 255.0.0.0
exit
interface Ethernet0/0/0
 no shutdown
 no switchport
 no ip address
exit
interface FastEthernet0
 no shutdown
 no switchport
 no ip address
exit
interface FastEthernet0/0
 no shutdown
 no switchport
 no ip address
exit
interface FastEthernet1/0
 no shutdown
 no switchport
 no ip address
exit
interface FastEthernet1/1
 no shutdown
 no switchport
 no ip address
exit
interface GigabitEthernet0
 no shutdown
 no switchport
 no ip address
exit
interface GigabitEthernet0/0
 no shutdown
 no switchport
 no ip address
exit
interface GigabitEthernet0/1
 no shutdown
 no switchport
 no ip address
exit
radius server one
 address ipv4 10.0.0.1 auth-port 1812 acct-port 1813
!
netsim_lab_gw#
admin@ncs#
```

Also note that for netsim devices since they are not a full router/switch, some commands may not function, even if they are valid IOS commands. This should not be an issue on an actual IOS device.
netsim
```
admin@ncs# devices device lab-gw0 live-status exec any "show ip route"
result
--------------------^
syntax error: element does not exist
netsim_lab_gw#
admin@ncs#
```

Now see work on actual IOS device:

```
admin@ncs# devices device svl-gem-lab-gw1 live-status exec any "show ip route"
```

# Now You try

Try sending a show command to your netsim device and a show command to a real IOS (your lab) device.
