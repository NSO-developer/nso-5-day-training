# Making a Simple QoS Config Template

To make a simple Service-template, we need a few things:
1. To know which parts of the config will change (what yang inputs we need, in this case keeping it simple with only devicename as a variable input, pulled from the NSO CDB)
2. The cut sheets for what config needs to be pushed
3. Any business logic that needs to be known and stored in yang

# The Cut sheets

For example, let's assume we have a cut sheet, like so:

Class-map
```
class-map match-all qos-voice-bearer
  match access-group name qos-voice-bearer
class-map match-all qos-scavenger
  match access-group name qos-scavenger
class-map match-all qos-signalling
  match access-group name qos-signalling
class-map match-all video-af42
  match access-group name qos-video-af42
class-map match-all video-af41
  match access-group name qos-video-af41
class-map match-all match-everything
  match access-group name trust-all
class-map match-all qos-medium-priority
  match access-group name qos-medium-priority
class-map match-all video-cs4
  match access-group name qos-video-cs4

table-map dscp2dscp
 default copy
```

ACL's

```
ip access-list extended qos-scavenger
 remark Traffic to be classify into scavenger
 remark SnapMirror
 remark SnapMirror Backup from remote DC to Hub location
 permit tcp any range 10565 10569 any
 remark SnapMirror Restore from remote DC to Hub location
 permit tcp any any range 10565 10569
 remark SnapVault Restore from remote DC to Hub location
 permit tcp any any range 11104 11105
 remark SnapVault Backup from remote DC to Hub location
 permit tcp any range 11104 11105 any
 remark PC Backup
 permit tcp any any eq 16384
 remark Crash-Plan-PC-Backup
 permit tcp any any eq 4282
 remark Beyond App Migration
 permit tcp any eq 49221 any
 remark Avamar
 permit tcp any eq 27000 any eq 27000
 remark Rsync over SSH
 permit tcp any any eq 873
 remark DD/ART, SCP, SFTP over SSH
 permit tcp any any eq 2222
 remark CDP & Recover Point
 permit tcp any any eq 5040
 remark FCIP & SRDF/A
 permit tcp any any eq 3225
 remark Celerra Replicator
 permit tcp any any eq 8888
 remark NMSP Traffic from WLC to MSE
 permit tcp any any eq 16113
!
ip access-list extended qos-medium-priority
 remark Placeholder for future use
!
ip access-list extended qos-signalling
 remark Traffic to be classify into Signalling
 remark Skinny
 permit tcp any any range 2000 2001
 remark Gatekeeper RAS, Q.931 and H.245 call set up
 permit udp any any eq 1719
 permit tcp any any eq 1720
 remark H.245
 permit tcp any any range 5555 5560
 remark SIP
 permit tcp any any range 5060 5061
 permit udp any any range 5060 5061
 remark RADIUS for EAP
 permit udp any any range 1645 1646
 permit udp any any range 1812 1813
!
ip access-list extended qos-video-af41
 remark Traffic to be classified as AF41
 remark Tandberg endpoints
 permit udp any range 2326 2485 any dscp 35
 permit udp any range 46000 49000 any dscp 35
!
ip access-list extended qos-video-af42
 remark Traffic to be classified as AF42
 remark Tandberg endpoints
 permit udp any range 2326 2485 any dscp 37
 permit udp any range 46000 49000 any dscp 37
 remark CUVA
 permit udp any any eq 5445
 remark Tandberg Movi
 permit udp any range 14040 14240 any
!
ip access-list extended qos-video-cs4
 remark Traffic to be classified as CS4
 remark Tandberg endpoints
 permit udp any range 2326 2485 any dscp 33
 permit udp any range 46000 49000 any dscp 33
!
ip access-list extended qos-voice-bearer
 remark Traffic to be classify into Voice-bearer
 remark IP Communicator
 permit udp any range 24576 32767 any
```

Policy-maps
```
policy-map classify
 description QoS 2.3.2 -
 class qos-scavenger
   set dscp cs1
 class qos-medium-priority
   set dscp cs2
 class qos-signalling
   set dscp cs3
 class video-cs4
   set dscp cs4
 class video-af41
   set dscp af41
 class video-af42
   set dscp af42
 class qos-voice-bearer
   set dscp ef
 class match-everything
   set dscp default

policy-map untrusted
 class class-default
   set dscp default

policy-map TRUST-MARKING
description trust-all
class class-default
   set dscp dscp table dscp2dscp
```

Interface-config
```
vlan configuration 10,300
 service-policy input classify
!
vlan configuration 240,550
 service-policy input untrusted
!
interface GigabitEthernet1/1
 service-policy input TRUST-MARKING
```


Now let's take that config and plug it into a netsim to get the XML representation of it.

```
JABELK-M-D3BK:nso-qos-no-python jabelk$ ncs-netsim create-device cisco-ios myqosdevice
DEVICE myqosdevice CREATED
JABELK-M-D3BK:nso-qos-no-python jabelk$ ls
load-dir		netsim			package-meta-data.xml	src			templates		test
JABELK-M-D3BK:nso-qos-no-python jabelk$ cd netsim/
JABELK-M-D3BK:netsim jabelk$ ncs-netsim start
DEVICE myqosdevice OK STARTED
JABELK-M-D3BK:netsim jabelk$ ncs-netsim cli-i myqosdevice

admin connected from 127.0.0.1 using console on JABELK-M-D3BK
myqosdevice> en
myqosdevice# conf
Enter configuration commands, one per line. End with CNTL/Z.
myqosdevice(config)#
```

If you already have a netsim running you can use that as well, and if it is running already, an error will throw.

Now copy your commands into your netsim, see if there are any syntax errors. If not, your end should look like this:

```
myqosdevice(config-vlan-config)# interface GigabitEthernet1/1
myqosdevice(config-if)#  service-policy input TRUST-MARKING
myqosdevice(config-if)# end
myqosdevice# write memory
```

# Syncing the config from the netsim to get the xml

Now do a sync-from from that netsim.

```
admin@ncs# devices device myqosdevice sync-from
admin@ncs# sync-from
result true
admin@ncs#
```

Now we can take the config of that device and export it to xml and save it to a file.

```
show running-config devices device myqosdevice config | display xml | save full_config.xml
```

This will save the output to the file, whereever you started the ncs_cli. Exit the ncs_cli and look at the full config XML.

If you wanted you could have exported just a portion of the config like so:

```
show running-config devices device myqosdevice config ios:class-map  | display xml | save some_config.xml
```

but in this case we are dealing with multiple sub-trees of information (interfaces, class-maps, etc.) so it will be easier to just extract it from the dummy netsim stuff.

- Now open your xml file in a text editor (ideally Atom/Sublime so you get text highlighting).

you will get something like this:

``` xml
<config xmlns="http://tail-f.com/ns/config/1.0">
  <devices xmlns="http://tail-f.com/ns/ncs">
  <device>
    <name>myqosdevice</name>
      <config>
        <tailfned xmlns="urn:ios">
          <police>cirmode</police>
        </tailfned>
        <aaa xmlns="urn:ios">
          <accounting>
            <delay-start>
            </delay-start>
          </accounting>
        </aaa>
        <ip xmlns="urn:ios">
          <source-route>true</source-route>
          <gratuitous-arps-conf>
            <gratuitous-arps>false</gratuitous-arps>
          </gratuitous-arps-conf>
          <finger>
          </finger>
          <http>
            <server>false</server>
            <secure-server>false</secure-server>
          </http>
          <access-list>
            <extended>
              <ext-named-acl>
                <name>qos-medium-priority</name>
                <ext-access-list-rule>
                  <rule>remark Placeholder for future use</rule>
                </ext-access-list-rule>
              </ext-named-acl>
              <ext-named-acl>
                <name>qos-scavenger</name>
                <ext-access-list-rule>
                  <rule>remark Traffic to be classify into scavenger</rule>
                </ext-access-list-rule>
                <ext-access-list-rule>
                  <rule>remark SnapMirror</rule>
                </ext-access-list-rule>
                <ext-access-list-rule>
                  <rule>remark SnapMirror Backup from remote DC to Hub location</rule>
                </ext-access-list-rule>
                <ext-access-list-rule>
                  <rule>permit tcp any range 10565 10569 any</rule>
                </ext-access-list-rule>
                <ext-access-list-rule>
                  <rule>remark SnapMirror Restore from remote DC to Hub location</rule>
                </ext-access-list-rule>
                <ext-access-list-rule>
                  <rule>permit tcp any any range 10565 10569</rule>
                </ext-access-list-rule>
                <ext-access-list-rule>
                  <rule>remark SnapVault Restore from remote DC to Hub location</rule>
                </ext-access-list-rule>
                <ext-access-list-rule>
                  <rule>permit tcp any any range 11104 11105</rule>
                </ext-access-list-rule>
                <ext-access-list-rule>
                  <rule>remark SnapVault Backup from remote DC to Hub location</rule>
                </ext-access-list-rule>
                <ext-access-list-rule>
                  <rule>permit tcp any range 11104 11105 any</rule>
                </ext-access-list-rule>
                <ext-access-list-rule>
                  <rule>remark PC Backup</rule>
                </ext-access-list-rule>
                <ext-access-list-rule>
                  <rule>permit tcp any any eq 16384</rule>
                </ext-access-list-rule>
                <ext-access-list-rule>
                  <rule>remark Crash-Plan-PC-Backup</rule>
                </ext-access-list-rule>
                <ext-access-list-rule>
                  <rule>permit tcp any any eq 4282</rule>
                </ext-access-list-rule>
                <ext-access-list-rule>
                  <rule>remark Beyond App Migration</rule>
                </ext-access-list-rule>
                <ext-access-list-rule>
                  <rule>permit tcp any eq 49221 any</rule>
                </ext-access-list-rule>
                <ext-access-list-rule>
                  <rule>remark Avamar</rule>
                </ext-access-list-rule>
                <ext-access-list-rule>
                  <rule>permit tcp any eq 27000 any eq 27000</rule>
                </ext-access-list-rule>
                <ext-access-list-rule>
                  <rule>remark Rsync over SSH</rule>
                </ext-access-list-rule>
                <ext-access-list-rule>
                  <rule>permit tcp any any eq 873</rule>
                </ext-access-list-rule>
                <ext-access-list-rule>
                  <rule>remark DD/ART, SCP, SFTP over SSH</rule>
                </ext-access-list-rule>
                <ext-access-list-rule>
                  <rule>permit tcp any any eq 2222</rule>
                </ext-access-list-rule>
                <ext-access-list-rule>
                  <rule>remark CDP &amp; Recover Point</rule>
                </ext-access-list-rule>
                <ext-access-list-rule>
                  <rule>permit tcp any any eq 5040</rule>
                </ext-access-list-rule>
                <ext-access-list-rule>
                  <rule>remark FCIP &amp; SRDF/A</rule>
                </ext-access-list-rule>
                <ext-access-list-rule>
                  <rule>permit tcp any any eq 3225</rule>
                </ext-access-list-rule>
                <ext-access-list-rule>
                  <rule>remark Celerra Replicator</rule>
                </ext-access-list-rule>
                <ext-access-list-rule>
                  <rule>permit tcp any any eq 8888</rule>
                </ext-access-list-rule>
                <ext-access-list-rule>
                  <rule>remark NMSP Traffic from WLC to MSE</rule>
                </ext-access-list-rule>
                <ext-access-list-rule>
                  <rule>permit tcp any any eq 16113</rule>
                </ext-access-list-rule>
              </ext-named-acl>
              <ext-named-acl>
                <name>qos-signalling</name>
                <ext-access-list-rule>
                  <rule>remark Traffic to be classify into Signalling</rule>
                </ext-access-list-rule>
                <ext-access-list-rule>
                  <rule>remark Skinny</rule>
                </ext-access-list-rule>
                <ext-access-list-rule>
                  <rule>permit tcp any any range 2000 2001</rule>
                </ext-access-list-rule>
                <ext-access-list-rule>
                  <rule>remark Gatekeeper RAS, Q.931 and H.245 call set up</rule>
                </ext-access-list-rule>
                <ext-access-list-rule>
                  <rule>permit udp any any eq 1719</rule>
                </ext-access-list-rule>
                <ext-access-list-rule>
                  <rule>permit tcp any any eq 1720</rule>
                </ext-access-list-rule>
                <ext-access-list-rule>
                  <rule>remark H.245</rule>
                </ext-access-list-rule>
                <ext-access-list-rule>
                  <rule>permit tcp any any range 5555 5560</rule>
                </ext-access-list-rule>
                <ext-access-list-rule>
                  <rule>remark SIP</rule>
                </ext-access-list-rule>
                <ext-access-list-rule>
                  <rule>permit tcp any any range 5060 5061</rule>
                </ext-access-list-rule>
                <ext-access-list-rule>
                  <rule>permit udp any any range 5060 5061</rule>
                </ext-access-list-rule>
                <ext-access-list-rule>
                  <rule>remark RADIUS for EAP</rule>
                </ext-access-list-rule>
                <ext-access-list-rule>
                  <rule>permit udp any any range 1645 1646</rule>
                </ext-access-list-rule>
                <ext-access-list-rule>
                  <rule>permit udp any any range 1812 1813</rule>
                </ext-access-list-rule>
              </ext-named-acl>
              <ext-named-acl>
                <name>qos-video-af41</name>
                <ext-access-list-rule>
                  <rule>remark Traffic to be classified as AF41</rule>
                </ext-access-list-rule>
                <ext-access-list-rule>
                  <rule>remark Tandberg endpoints</rule>
                </ext-access-list-rule>
                <ext-access-list-rule>
                  <rule>permit udp any range 2326 2485 any dscp 35</rule>
                </ext-access-list-rule>
                <ext-access-list-rule>
                  <rule>permit udp any range 46000 49000 any dscp 35</rule>
                </ext-access-list-rule>
              </ext-named-acl>
              <ext-named-acl>
                <name>qos-video-af42</name>
                <ext-access-list-rule>
                  <rule>remark Traffic to be classified as AF42</rule>
                </ext-access-list-rule>
                <ext-access-list-rule>
                  <rule>remark Tandberg endpoints</rule>
                </ext-access-list-rule>
                <ext-access-list-rule>
                  <rule>permit udp any range 2326 2485 any dscp 37</rule>
                </ext-access-list-rule>
                <ext-access-list-rule>
                  <rule>permit udp any range 46000 49000 any dscp 37</rule>
                </ext-access-list-rule>
                <ext-access-list-rule>
                  <rule>remark CUVA</rule>
                </ext-access-list-rule>
                <ext-access-list-rule>
                  <rule>permit udp any any eq 5445</rule>
                </ext-access-list-rule>
                <ext-access-list-rule>
                  <rule>remark Tandberg Movi</rule>
                </ext-access-list-rule>
                <ext-access-list-rule>
                  <rule>permit udp any range 14040 14240 any</rule>
                </ext-access-list-rule>
              </ext-named-acl>
              <ext-named-acl>
                <name>qos-video-cs4</name>
                <ext-access-list-rule>
                  <rule>remark Traffic to be classified as CS4</rule>
                </ext-access-list-rule>
                <ext-access-list-rule>
                  <rule>remark Tandberg endpoints</rule>
                </ext-access-list-rule>
                <ext-access-list-rule>
                  <rule>permit udp any range 2326 2485 any dscp 33</rule>
                </ext-access-list-rule>
                <ext-access-list-rule>
                  <rule>permit udp any range 46000 49000 any dscp 33</rule>
                </ext-access-list-rule>
              </ext-named-acl>
              <ext-named-acl>
                <name>qos-voice-bearer</name>
                <ext-access-list-rule>
                  <rule>remark Traffic to be classify into Voice-bearer</rule>
                </ext-access-list-rule>
                <ext-access-list-rule>
                  <rule>remark IP Communicator</rule>
                </ext-access-list-rule>
                <ext-access-list-rule>
                  <rule>permit udp any range 24576 32767 any</rule>
                </ext-access-list-rule>
              </ext-named-acl>
            </extended>
          </access-list>
        </ip>
        <table-map xmlns="urn:ios">
          <name>dscp2dscp</name>
          <default>copy</default>
        </table-map>
        <class-map xmlns="urn:ios">
          <name>match-everything</name>
          <prematch>match-all</prematch>
          <match>
            <access-group>
              <name>trust-all</name>
            </access-group>
          </match>
        </class-map>
        <class-map xmlns="urn:ios">
          <name>qos-medium-priority</name>
          <prematch>match-all</prematch>
          <match>
            <access-group>
              <name>qos-medium-priority</name>
            </access-group>
          </match>
        </class-map>
        <class-map xmlns="urn:ios">
          <name>qos-scavenger</name>
          <prematch>match-all</prematch>
          <match>
            <access-group>
              <name>qos-scavenger</name>
            </access-group>
          </match>
        </class-map>
        <class-map xmlns="urn:ios">
          <name>qos-signalling</name>
          <prematch>match-all</prematch>
          <match>
            <access-group>
              <name>qos-signalling</name>
            </access-group>
          </match>
        </class-map>
        <class-map xmlns="urn:ios">
          <name>qos-voice-bearer</name>
          <prematch>match-all</prematch>
          <match>
            <access-group>
              <name>qos-voice-bearer</name>
            </access-group>
          </match>
        </class-map>
        <class-map xmlns="urn:ios">
          <name>video-af41</name>
          <prematch>match-all</prematch>
          <match>
            <access-group>
              <name>qos-video-af41</name>
            </access-group>
          </match>
        </class-map>
        <class-map xmlns="urn:ios">
          <name>video-af42</name>
          <prematch>match-all</prematch>
          <match>
            <access-group>
              <name>qos-video-af42</name>
            </access-group>
          </match>
        </class-map>
        <class-map xmlns="urn:ios">
          <name>video-cs4</name>
          <prematch>match-all</prematch>
          <match>
            <access-group>
              <name>qos-video-cs4</name>
            </access-group>
          </match>
        </class-map>
        <vlan xmlns="urn:ios">
          <configuration>
            <id>10</id>
            <service-policy>
              <input>classify</input>
            </service-policy>
          </configuration>
          <configuration>
            <id>240</id>
            <service-policy>
              <input>untrusted</input>
            </service-policy>
          </configuration>
          <configuration>
            <id>300</id>
            <service-policy>
              <input>classify</input>
            </service-policy>
          </configuration>
          <configuration>
            <id>550</id>
            <service-policy>
              <input>untrusted</input>
            </service-policy>
          </configuration>
        </vlan>
        <interface xmlns="urn:ios">
          <Loopback>
            <name>0</name>
            <ip>
              <address>
                <primary>
                  <address>127.0.0.1</address>
                  <mask>255.0.0.0</mask>
                </primary>
              </address>
            </ip>
          </Loopback>
          <Ethernet>
            <name>0/0/0</name>
            <ip>
              <no-address>
                <address>false</address>
              </no-address>
            </ip>
          </Ethernet>
          <FastEthernet>
            <name>0</name>
            <ip>
              <no-address>
                <address>false</address>
              </no-address>
            </ip>
          </FastEthernet>
          <FastEthernet>
            <name>0/0</name>
            <ip>
              <no-address>
                <address>false</address>
              </no-address>
            </ip>
          </FastEthernet>
          <FastEthernet>
            <name>1/0</name>
            <ip>
              <no-address>
                <address>false</address>
              </no-address>
            </ip>
          </FastEthernet>
          <FastEthernet>
            <name>1/1</name>
            <ip>
              <no-address>
                <address>false</address>
              </no-address>
            </ip>
          </FastEthernet>
          <GigabitEthernet>
            <name>0</name>
            <ip>
              <no-address>
                <address>false</address>
              </no-address>
            </ip>
          </GigabitEthernet>
          <GigabitEthernet>
            <name>0/0</name>
            <ip>
              <no-address>
                <address>false</address>
              </no-address>
            </ip>
          </GigabitEthernet>
          <GigabitEthernet>
            <name>0/1</name>
            <ip>
              <no-address>
                <address>false</address>
              </no-address>
            </ip>
          </GigabitEthernet>
          <GigabitEthernet>
            <name>1/1</name>
            <service-policy>
              <input>TRUST-MARKING</input>
            </service-policy>
          </GigabitEthernet>
        </interface>
      </config>
  </device>
  </devices>
</config>
```

This is where a working knowledge of reading xml comes in handy. You can easily extract the config parts that relate to your config by removing the default netsim data


remove these parts (Take a minute to look over why I chose them, look at the cut sheets as compared to what we are trying to enforce, this stuff is just extra running-config, we don't want as part of the template, a more surgical specific show command would have made this easier) :
``` xml
<config xmlns="http://tail-f.com/ns/config/1.0">
  <devices xmlns="http://tail-f.com/ns/ncs">
  <device>
    <name>myqosdevice</name>
      <config>
        <tailfned xmlns="urn:ios">
          <police>cirmode</police>
        </tailfned>
        <aaa xmlns="urn:ios">
          <accounting>
            <delay-start>
            </delay-start>
          </accounting>
        </aaa>
        <ip xmlns="urn:ios">
          <source-route>true</source-route>
          <gratuitous-arps-conf>
            <gratuitous-arps>false</gratuitous-arps>
          </gratuitous-arps-conf>
          <finger>
          </finger>
          <http>
            <server>false</server>
            <secure-server>false</secure-server>
          </http>

          <Loopback>
            <name>0</name>
            <ip>
              <address>
                <primary>
                  <address>127.0.0.1</address>
                  <mask>255.0.0.0</mask>
                </primary>
              </address>
            </ip>
          </Loopback>
          <Ethernet>
            <name>0/0/0</name>
            <ip>
              <no-address>
                <address>false</address>
              </no-address>
            </ip>
          </Ethernet>
          <FastEthernet>
            <name>0</name>
            <ip>
              <no-address>
                <address>false</address>
              </no-address>
            </ip>
          </FastEthernet>
          <FastEthernet>
            <name>0/0</name>
            <ip>
              <no-address>
                <address>false</address>
              </no-address>
            </ip>
          </FastEthernet>
          <FastEthernet>
            <name>1/0</name>
            <ip>
              <no-address>
                <address>false</address>
              </no-address>
            </ip>
          </FastEthernet>
          <FastEthernet>
            <name>1/1</name>
            <ip>
              <no-address>
                <address>false</address>
              </no-address>
            </ip>
          </FastEthernet>
          <GigabitEthernet>
            <name>0</name>
            <ip>
              <no-address>
                <address>false</address>
              </no-address>
            </ip>
          </GigabitEthernet>
          <GigabitEthernet>
            <name>0/0</name>
            <ip>
              <no-address>
                <address>false</address>
              </no-address>
            </ip>
          </GigabitEthernet>
          <GigabitEthernet>
            <name>0/1</name>
            <ip>
              <no-address>
                <address>false</address>
              </no-address>
            </ip>
          </GigabitEthernet>


        </config>
    </device>
    </devices>
  </config>
```

# Making the service package
Now that we have the XML we can create the service-skeleton

```
cd ncs-run
cd packages
ncs-make-package --service-skeleton template nso-qos-no-python --augment /ncs:services
```

This service-skeleton creates a package file structure with a complete yang module which has a leafref to the device list, and a basic leaf node expecting an IP address. The device list is nested within a list of service instances. In order to make the service-skeleton work you will need to add one more piece of information.

- add "augment /ncs:services " to before the list of the service name (see below for snippet), and also *make sure* to add a closing bracket at the bottom since we are encapsulating the list in the services augment. I added a comment to point out which one I added at the bottom.

```
import tailf-ncs {
  prefix ncs;
}


augment /ncs:services {

list nso-qos-no-python {
  key name;

  uses ncs:service-data;
  ncs:servicepoint "nso-qos-no-python";

  leaf name {
    type string;
  }

  // may replace this with other ways of refering to the devices.
  leaf-list device {
    type leafref {
      path "/ncs:devices/ncs:device/ncs:name";
    }
  }

  // replace with your own stuff here
  leaf dummy {
    type inet:ipv4-address;
  }
}
} //for augment services close
}

```

This statement tells the NSO yang (ncs namespace) to take our existing model and plug it into the NSO application services.

# Inserting your XML config into the XML template

- You should have an edited XML file, which removed the parts of the config that were specific to the netsim and are not supposed to be a part of the config. Make sure that you got the ip beginning and ending tags for the ip access-list, because the ip tag has several other things in it that makes it easy to miss.

Open the auto-generated XML template file in the nso-qos-no-python/templates/nso-qos-no-python-template.xml

it should look like this:
``` xml
<config-template xmlns="http://tail-f.com/ns/config/1.0"
                 servicepoint="nso-qos-no-python">
  <devices xmlns="http://tail-f.com/ns/ncs">
    <device>
      <!--
          Select the devices from some data structure in the service
          model. In this skeleton the devices are specified in a leaf-list.
          Select all devices in that leaf-list:
      -->
      <name>{/device}</name>
      <config>
        <!--
            Add device-specific parameters here.
            In this skeleton the service has a leaf "dummy"; use that
            to set something on the device e.g.:
            <ip-address-on-device>{/dummy}</ip-address-on-device>
        -->
      </config>
    </device>
  </devices>
</config-template>
```

Now insert all of your XML config into the nested config tag

``` xml
<config-template xmlns="http://tail-f.com/ns/config/1.0"
                 servicepoint="nso-qos-no-python">
  <devices xmlns="http://tail-f.com/ns/ncs">
    <device>
      <name>{/device}</name>
<config>
COPY AND PASTE HERE
</config>
</device>
</devices>
</config-template>

```

-

# Integrating it into the NSO application

Now change directory to the src folder and reload the packages. We do not need to run the make command because we did not change the yang.

```
JABELK-M-D3BK:src jabelk$ ncs_cli -C -u admin

admin connected from 127.0.0.1 using console on JABELK-M-D3BK
admin@ncs# packages reload

>>> System upgrade is starting.
>>> Sessions in configure mode must exit to operational mode.
>>> No configuration changes can be performed until upgrade has completed.
>>> System upgrade has completed successfully.
reload-result {
    package bgl-test
    result true
}
reload-result {
    package cisco-ios
    result true
}
reload-result {
    package nso-qos-no-python
    result true
}
admin@ncs#
System message at 2017-10-24 17:17:19...
    Subsystem stopped: ncs-dp-8-cisco-ios:IOSDp

System message at 2017-10-24 17:17:19...
    Subsystem started: ncs-dp-9-cisco-ios:IOSDp
admin@ncs# admin@ncs#
```

So now we have the service yang model integrated into NSO's services, and we have the template connected to that service-model and now we just need to create a service instance, adding some devices to it.

# Creating a service-instance

Since the service model assumes a list, with a unique identifier for each service instance, we need to create a unique id (either through GUI/CLI etc):

if we enter NSO CLI and go into configure mode we can see our service under the services options:

```
admin@ncs(config)# services ?
Possible completions:
  check-sync           Check if device configuration is according to the services
  commit-dry-run       DEPRECATED - use commit dry-run instead
  customer-service     Service that can be linked to customer
  global-settings
  logging              Configure service logging
  nso-qos-no-python
  plan-notifications   Configuration to send plan-state-change notifications for plan state transitions.
  service              List of resource facing services
admin@ncs(config)# services
```

Now we give it a unique ID for a service instance

```
admin@ncs(config)# services nso-qos-no-python LD_SITE_INSTANCE
admin@ncs(config-nso-qos-no-python-LD_SITE_INSTANCE)# ?
Possible completions:
  check-sync           Check if device config is according to the service
  commit-queue
  deep-check-sync      Check if device config is according to the service
  device
  dummy
  get-modifications    Get the data this service created
  log
  re-deploy            Run/Dryrun the service logic again
  reactive-re-deploy   Reactive redeploy of service logic
  touch                Touch a service
  un-deploy            Undo the effects of this service
  ---
  commit               Commit current set of changes
  describe             Display transparent command information
  exit                 Exit from current mode
  help                 Provide help information
  no                   Negate a command or set its defaults
  pwd                  Display current mode path
  rload                Load configuration from an ASCII file relative to current location
  top                  Exit to top level and optionally run command
admin@ncs(config-nso-qos-no-python-LD_SITE_INSTANCE)#
```

We can see a lot of default options for services, along with our 2 inputs from our yang model:
- device (which is a leafref to our NSO CDB devices list)
- dummy (which is a random leaf that does nothing in our service)

Let's add a device to the service and commit dry run to see what the changes would be
```
admin@ncs(config)# services nso-qos-no-python LD_SITE_INSTANCE device myqosdevice
admin@ncs(config-nso-qos-no-python-LD_SITE_INSTANCE)# commit dry-run
cli {
    local-node {
        data  devices {
                  device myqosdevice {
                      config {
                          ios:ip {
                              access-list {
                                  extended {
             +                        ext-named-acl qos-medium-priority {
             +                            ext-access-list-rule "remark Placeholder for future use";
             +                        }
                                      ext-named-acl qos-scavenger {
                                      }
                                      ext-named-acl qos-signalling {
                                      }
                                      ext-named-acl qos-video-af41 {
             +                            # after ext-access-list-rule "remark Spark client and endpoint to cloud or HMN"
             +                            ext-access-list-rule "permit udp any range 52100 52299 any eq 5004 ";
                                      }
                                      ext-named-acl qos-video-af42 {
                                      }
                                      ext-named-acl qos-video-cs4 {
                                      }
                                      ext-named-acl qos-voice-bearer {
             +                            # after ext-access-list-rule "remark Spark client and endpoint to cloud or HMN"
             +                            ext-access-list-rule "permit udp any range 52000 52099 any eq 5004 ";
                                      }
                                  }
                              }
                          }
                          ios:class-map match-everything {
                          }
                          ios:class-map medium-priority {
                          }
                          ios:class-map scavenger {
                          }
                          ios:class-map signalling {
                          }
                          ios:class-map video-af41 {
                          }
                          ios:class-map video-af42 {
                          }
                          ios:class-map video-bearer {
                          }
                          ios:class-map video-cs4 {
                          }
                          ios:class-map voice-bearer {
                          }
                          ios:policy-map classify {
                          }
                          ios:policy-map untrusted {
                          }
                          ios:vlan {
                              configuration 10 {
                              }
                              configuration 240 {
                              }
                              configuration 300 {
                              }
                              configuration 550 {
                              }
                          }
                          ios:interface {
                              GigabitEthernet 1/1 {
                              }
                              GigabitEthernet 2/1 {
                              }
                          }
                      }
                  }
              }
              services {
             +    nso-qos-no-python LD_SITE_INSTANCE {
             +        device [ myqosdevice ];
             +    }
              }
    }
}
admin@ncs(config-nso-qos-no-python-LD_SITE_INSTANCE)#
```

This shows that my netsim device would have all that configuration added to it in order for it to be in compliance with the template I have associated with this service, given the input variables. You could add multiple devices to a service instance using the [ ] notation, separating them with spaces.

If part of the config was already present, only the difference between the template and the on device info would be applied.

In this example, I have actually done some out of band changes (from our first step, getting the XML info for the template), so If I try to push the service template on my netsim (yours may be different), it will complain the device is out of sync.

NSO realized that there was a difference between the local CDB and what was actually on my device.

So I need to a do a sync-from before initiating my sevice instance, and cancel this transaction.

```
admin@ncs(config-nso-qos-no-python-LD_SITE_INSTANCE)# commit
Aborted: Network Element Driver: device myqosdevice: out of sync
admin@ncs(config-nso-qos-no-python-LD_SITE_INSTANCE)# *** ALARM out-of-sync: Device myqosdevice is out of sync
admin@ncs(config-nso-qos-no-python-LD_SITE_INSTANCE)# end
Uncommitted changes found, commit them? [yes/no/CANCEL] no
admin@ncs# devices device myqosdevice sync-from
result true
admin@ncs#
```

# Trying again to push the service instance template

- Since I am starting a new transaction, I need to re-add my device to a new service instance that was cancelled from before:

```
admin@ncs# conf
Entering configuration mode terminal
admin@ncs(config)# services nso-qos-no-python LD_SITE_INSTANCE device myqosdevice
admin@ncs(config-nso-qos-no-python-LD_SITE_INSTANCE)# commit dry-run outformat native
native {
    device {
        name myqosdevice
        data ip access-list extended qos-medium-priority
              remark Placeholder for future use
             exit
             ip access-list extended qos-scavenger
              no remark Beyond App Migration
              no permit tcp any eq 49221 any
              no remark Avamar
              no permit tcp any eq 27000 any eq 27000
              no remark Rsync over SSH
              no permit tcp any any eq 873
              no remark DD/ART, SCP, SFTP over SSH
              no permit tcp any any eq 2222
              no remark CDP & Recover Point
              no permit tcp any any eq 5040
              no remark FCIP & SRDF/A
              no permit tcp any any eq 3225
              no remark Celerra Replicator
              no permit tcp any any eq 8888
              no remark NMSP Traffic from WLC to MSE
              no permit tcp any any eq 16113
              remark Crash-Plan-PC-Restore
              permit tcp any eq 4282 any
              remark Beyond App Migration
              permit tcp any eq 49221 any
              remark Avamar
              permit tcp any eq 27000 any eq 27000
              remark Rsync over SSH
              permit tcp any any eq 873
              remark DD/ART, SCP, SFTP over SSH
              permit tcp any any eq 2222
              remark CDP & Recover Point
              permit tcp any any eq 5040
              remark FCios:ip & SRDF/A
              remark FCIP & SRDF/A
              permit tcp any any eq 3225
              remark Celerra Replicator
              permit tcp any any eq 8888
              remark NMSP Traffic from WLC to MSE
              permit tcp any any eq 16113
             exit
             ip access-list extended qos-signalling
              remark Traffic to be classify into signalling
             exit
             ip access-list extended qos-video-af41
              no permit udp any range 52100 52299 any eq 5004
              remark Spark client and endpoint to cloud or HMN
              permit udp any range 52100 52299 any eq 5004
              remark Spark call endpoint to collaboration cloud
              permit udp any range 52200 52299 any eq 3478
              remark Spark Catch-all - to be removed once all Spark devices use the defined ports
              permit udp any any eq 3478
              permit udp any any eq 5004
              permit udp any range 52100 52299 any eq 5004
             exit
             ip access-list extended qos-voice-bearer
              no permit udp any range 52000 52099 any eq 5004
              remark Spark client and endpoint to cloud or HMN
              permit udp any range 52000 52099 any eq 5004
              remark Spark call endpoint to collaboration cloud
              permit udp any range 52050 52099 any eq 3478
              permit udp any range 52000 52099 any eq 5004
              remark Traffic to be classify into voice-bearer
              remark ios:ip Communicator
             exit
             class-map match-all medium-priority
              match access-group name qos-medium-priority
             !
             class-map match-all scavenger
              match access-group name qos-scavenger
             !
             class-map match-all signalling
              match access-group name qos-signalling
             !
             class-map match-all video-bearer
              match access-group name qos-video-bearer
             !
             class-map match-all voice-bearer
              match access-group name qos-voice-bearer
             !
             policy-map classify
              description "QoS 2.3.2-"
              class qos-scavenger
               set dscp 8
              !
              class qos-medium-priority
               set dscp 16
              !
              class qos-signalling
               set dscp 24
              !
              class qos-video-cs4
               set dscp cs4
              !
              class qos-video-af41
               set dscp af41
              !
              class qos-video-af42
               set dscp af42
              !
              class qos-voice-bearer
               set dscp 46
              !
             !
             policy-map untrusted
              class class-default
               set dscp default
              !
             !
             interface GigabitEthernet2/1
              service-policy input TRUST-MARKING
              no switchport
              no shutdown
             exit
    }
}
```
- after seeing the commit dry run, I see what the differnece is, and now actually commit the change:

```
admin@ncs(config-nso-qos-no-python-LD_SITE_INSTANCE)# commit
Commit complete.
```

# Now you try

- Make an out of band change on the device, logging in through a separate ssh session, and remove a piece of the config that the template is looking for, try re-deploying the service, to see it re-enforce the template.

```
JABELK-M-D3BK:myqosdevice jabelk$ ncs-netsim cli-i myqosdevice

admin connected from 127.0.0.1 using console on JABELK-M-D3BK
myqosdevice> en
myqosdevice# conf
Enter configuration commands, one per line. End with CNTL/Z.
myqosdevice(config)# no class-map match-all medium-priority
myqosdevice(config)# no ip access-list extended qos-medium-priority
myqosdevice(config)#
myqosdevice(config)# end
myqosdevice# write memory
myqosdevice# exit

**made a change**

admin@ncs# devices device myqosdevice sync-from
result true
admin@ncs# conf
admin@ncs(config)# services nso-qos-no-python LD_SITE_INSTANCE check-sync deep outformat native
native {
    device {
        name myqosdevice
        data

              ip access-list extended qos-medium-priority
               remark Placeholder for future use
              exit
              ip access-list extended qos-video-af41
               no permit udp any range 52100 52299 any eq 5004
               no remark Spark call endpoint to collaboration cloud
               no permit udp any range 52200 52299 any eq 3478
               no remark Spark Catch-all - to be removed once all Spark devices use the defined ports
               no permit udp any any eq 3478
               no permit udp any any eq 5004
               permit udp any range 52100 52299 any eq 5004
               remark Spark call endpoint to collaboration cloud
               permit udp any range 52200 52299 any eq 3478
               remark Spark Catch-all - to be removed once all Spark devices use the defined ports
               permit udp any any eq 3478
               permit udp any any eq 5004
               permit udp any range 52100 52299 any eq 5004
              exit
              ip access-list extended qos-voice-bearer
               no permit udp any range 52000 52099 any eq 5004
               no remark Spark call endpoint to collaboration cloud
               no permit udp any range 52050 52099 any eq 3478
               no remark Traffic to be classify into voice-bearer
               no remark ios:ip Communicator
               permit udp any range 52000 52099 any eq 5004
               remark Spark call endpoint to collaboration cloud
               permit udp any range 52050 52099 any eq 3478
               permit udp any range 52000 52099 any eq 5004
               remark Traffic to be classify into voice-bearer
               remark ios:ip Communicator
              exit
              class-map match-all medium-priority
               match access-group name qos-medium-priority
              !

    }
}
admin@ncs(config)#
```

The above command checks to see what the difference is between the device and the template.

```
admin@ncs(config)# services nso-qos-no-python LD_SITE_INSTANCE re-deploy
admin@ncs(config)# services nso-qos-no-python LD_SITE_INSTANCE check-sync deep outformat native
native {
}
admin@ncs(config)#
```

Now the device is in compliance.

## Also Try

- Now try adding your SVL device to the service, log in to the SVL device over SSH, do some show commands, see what is on there for the config for QoS. Then re-deploy the service with the new device added to the existing service instance.
