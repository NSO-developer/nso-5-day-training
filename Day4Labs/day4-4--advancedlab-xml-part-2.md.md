# ACL Interface Compliance Service Model - XML

This Lab will go through building the XML template for the ACL Application Use Case. We will just cover IPv4 for this lab.

## Requirements

The template will map the inputed model data per device, per interface into the config:

```
interface {Interface_type}{interface_number}
  ip access-group {acl_name}{ACL_Direction}
```

```
interface GigabitEthernet0/0
  ip access-group test_acl in
```

## Quick introduction NSO Service Templates

The NSO Template engine enables for quick and easy dynamic templates.

The templates are very powerful but have their own syntax.

To do a "if" type statement:
XML templates allow for if type logic through 'when' statements inside desired XML blocks. This allows us to apply types of config based on inputted info:
```xml
<FastEthernet when="{/devices/interfaces/interface_type='FastEthernet'">
    Anything inside these blocks are applied 'IF' / 'WHEN' FastEthernet is selected
</FastEthernet>
```
To do a "for" type statement:

for example to loop over each inputted device from a YANG model  may look like below:

```xml
<device foreach={/devices}>
  Everything inside these tags are repeated 'for' / 'foreach' device in the devices list.
  we then access the variables the the devices list via {variable_name} convention.
</device>
```

## Template Planning

For our templates we some logic that needs to be applied.

We need to apply the interface config 'foreach' interface entered, for each device entered. Then we need to apply the template specific interface types dependent upon selected type inside the interface foreach.

Model:
```python
for device in devices
  for interface in interfaces
    apply to GigEthernet "if/when" int_type = GigEthernet
    apply to FastEthernet "if/when" int_type = FastEthernet
    etc...
```

We then also need to get our XML representation of the intended config.

## Build the Template

Our first task should be to gnerate the XML structure needed for our configuration.
NSO makes this easy with the NSO CLI.

We need to use the NSO CLI to enter the config into a device, then use the `commit dry-run outformat xml` to get our inputted CLI in XML format.

Or we can sync-from a device knwon to have the config, the use a show running-config display xml command tog et the config in XML.

We will enter the commands via CLI.

The CLI is:
```
interface GigabitEthernet0/0
  ip access-group test_acl in
```

In the NSO CLI config mode:
```
admin@ncs(config)# devices device lab-gw0 config    
admin@ncs(config-config)# ios:interface GigabitEthernet 0/0
admin@ncs(config-if)# ip access-group test_acl in      
admin@ncs(config-if)# commit dry-run outformat xml     
result-xml {
    local-node {
        data <devices xmlns="http://tail-f.com/ns/ncs">
               <device>
                 <name>lab-gw0</name>
                 <config>
                   <interface xmlns="urn:ios">
                     <GigabitEthernet>
                       <name>0/0</name>
                       <ip>
                         <access-group>
                           <direction>in</direction>
                           <access-list>test_acl</access-list>
                         </access-group>
                       </ip>
                     </GigabitEthernet>
                   </interface>
                 </config>
               </device>
             </devices>
    }
}
admin@ncs(config-if)#
```

We will then use this as our template with variables.


Our first for-loop will be for each device in the device list.

Updating the skeleton template we have:
```xml
<config-template xmlns="http://tail-f.com/ns/config/1.0"
                 servicepoint="acl_lab">
  <devices xmlns="http://tail-f.com/ns/ncs">
    <device foreach="{/devices}">
      <name>{device_name}</name>
      <config>
      </config>
    </device>
  </devices>
</config-template>
```

What this XML template is saying is:

For each device entered into our YANG Model, modify the NSO instance of the device by referencing the device_name variable from our YANG model.

Our Second for-loop is the interface loop. We want to apply our template foreach interface entered in for that device.
```xml
<config-template xmlns="http://tail-f.com/ns/config/1.0"
                 servicepoint="acl_lab">
  <devices xmlns="http://tail-f.com/ns/ncs">
    <device foreach="{/devices}">
      <name>{device_name}</name>
      <config>
        <interface xmlns="urn:ios" foreach="{interfaces}" >
        </interface>
      </config>
    </device>
  </devices>
</config-template>
```

Note that the foreach={interfaces} does not begin with a / as '/' represents from the root node.

Now we need to conduct our if/when logic for determining which interface type to apply to:
```xml
<interface xmlns="urn:ios" foreach="{interfaces}" >
  <FastEthernet when="{interface_type='FastEthernet'}">
  </FastEthernet>

  <GigabitEthernet when="{interface_type='GigabitEthernet'}">
  </GigabitEthernet>

  <TenGigabitEthernet when="{interface_type='TenGigabitEthernet'}">
  </TenGigabitEthernet>

  <Tunnel when="{interface_type='Tunnel'}">
  </Tunnel>
</interface>
```

So far, we have created our loops for the devices, the interfaces and created our if/when logic.
Now to populate our template.

For our use case we will apply the IPv4 ACL in the specified direction into the XML template created.

Inside each interface type block add the ACL XML with variables. Notice that the ACL variables begin with a /, as the variable information is at the root of our model.

```xml
<name>{interface_number}</name>
<ip>
    <access-group tags="merge">
        <direction>{/ACL_Direction}</direction>
        <access-list>{/ACL_Name}</access-list>
    </access-group>
</ip>
```

If done correctly, the template should look something like:
```xml
<config-template xmlns="http://tail-f.com/ns/config/1.0"
                 servicepoint="acl_lab">
  <devices xmlns="http://tail-f.com/ns/ncs">
    <device foreach="{/devices}">
      <name>{device_name}</name>
      <config>
        <interface xmlns="urn:ios" foreach="{interfaces}" >
          <FastEthernet when="{interface_type='FastEthernet'}">
            <name>{interface_number}</name>
            <ip>
              <access-group tags="merge">
                  <direction>{/ACL_Direction}</direction>
                  <access-list>{/ACL_Name}</access-list>
              </access-group>
            </ip>
          </FastEthernet>
          <GigabitEthernet when="{interface_type='GigabitEthernet'}">
            <name>{interface_number}</name>
            <ip>
              <access-group tags="merge">
                  <direction>{/ACL_Direction}</direction>
                  <access-list>{/ACL_Name}</access-list>
              </access-group>
            </ip>
          </GigabitEthernet>

          <TenGigabitEthernet when="{interface_type='TenGigabitEthernet'}">
            <name>{interface_number}</name>
            <ip>
              <access-group tags="merge">
                  <direction>{/ACL_Direction}</direction>
                  <access-list>{/ACL_Name}</access-list>
              </access-group>
            </ip>
          </TenGigabitEthernet>

          <Tunnel when="{interface_type='Tunnel'}">
            <name>{interface_number}</name>
            <ip>
              <access-group tags="merge">
                  <direction>{/ACL_Direction}</direction>
                  <access-list>{/ACL_Name}</access-list>
              </access-group>
            </ip>
          </Tunnel>
        </interface>
      </config>
    </device>
  </devices>
</config-template>
```

## Loading the Package

Now that we have a completed YANG Model & XML Template mapping to it, we are ready to load and test our application.

Enter the NSO CLI: `ncs_cli -C -u admin`

Then enter the packages reload command: `packages reload`

You should see a reload result of true:

```bash
reload-result {
    package acl_lab
    result true
}
```

If your template had errors, you will see an error message of what was wrong after the result tab:

example:
```bash
reload-result {
    package acl_lab
    result false
    info [acl_lab-template.xml:4: The string "{/devices}>\n      <name>{device_name}</name>\n      <config>\n        <interface xmlns=\"urn:ios\" >\n          <FastEthernet foreach=\"{/interfaces}\" when=\"{/interfaces/interface_type='FastEthernet'}\">\n              <name>{interfaceNumber}</name>\n              <ip>\n                  <access-group tags=\"merge\">\n                      <direction>out</direction>\n                      <access-list>lab-lenient</access-list>\n                  </access-group>\n              </ip>\n              <ipv6>\n                  <traffic-filter tags=\"merge\">\n                      <direction>out</direction>\n                      <access-list>lab-lenient-ipv6</access-list>\n                  </traffic-filter>\n              </ipv6>\n          </FastEthernet>\n        </interface>\n      </config>\n    </device>\n  </devices>\n</config-template>\n" is incorrectly quoted.]
}
```

In this example there was an uncompleted string "" that rendered most of the template as a string!

If you package reloaded as true then congratulations! You just built an NSO application for enforcing ACL Compliance.

Now we are ready to test our application.

## Recap

In summary we:
1. Created an XML configuration template
2. Applied loop logic to the template
3. Applied If/When logic to the template
4. Loaded are completed package into NSO


## Advanced Topic - Multi-Platform

So Far we have only applied this configuration to a Cisco IOS device.

However, we may want to enable this to apply the same configuration across multiple device types, be it Nexus, ASA or even other vendors.

NSO Enables us to do this with ease through the NED and Namespace constructs.

All that would be required is adding additional configurations to our template for additional devices.
