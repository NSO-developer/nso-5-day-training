# Day 2 Lab 1 - Navigating Structured Config Data

In this lab we will be navigating the NSO Config data structure through several different ways of viewing the data. This will help us visualize and understand how to navigate configuration data in NSO.

We will use the IOS command:

```
ipv6 unicast-routing
```



# Step 1 - Configure on the device

Lets start by enabling ipv6 unicast-routing on our ios netsim.

Log into the netsim CLI:
```
ncs-netsim cli-i your_netsim_name
netsim_lab_gw> enable
netsim_lab_gw# config
Enter configuration commands, one per line. End with CNTL/Z.
netsim_lab_gw(config)# ipv6 unicast-routing
netsim_lab_gw(config)#
```

Now lets view the running config to confirm its there:

```
netsim_lab_gw# show running-config | include ipv6
ipv6 unicast-routing
no ipv6 cef
```
# Step 2 - View in NSO CLI

Lets start by syncing the device with our NSO from the NSO CLI:

```
ncs_cli -C -u admin
admin@ncs# devices device your_netsim_name sync-from
result true
```

Now lets view our ipv6 unicast-routing config in its different representations.

Show the native cisco CLI via:
```
admin@ncs# show running-config devices device lab-gw0 config ios:ipv6           
devices device lab-gw0
 config
  ios:ipv6 unicast-routing
  no ios:ipv6 cef
 !
!
```

Then, lets see what our other display/representation options are:
```
admin@ncs# show running-config devices device lab-gw0 config ios:ipv6 | display ?     
Possible completions:
  annotations         Display annotations
  curly-braces        Display output as curly braces
  json                Display output as json
  keypath             Display output as keypath
  prefixes            Display namespace prefixes
  service-meta-data   Display service meta information
  tags                Display tags
  xml                 Display output as XML
  xpath               Display output as xpath
```

Lets start by looking at the config for ipv6 in xml:

```xml
admin@ncs# show running-config devices device lab-gw0 config ios:ipv6  | display xml
<config xmlns="http://tail-f.com/ns/config/1.0">
  <devices xmlns="http://tail-f.com/ns/ncs">
  <device>
    <name>lab-gw0</name>
      <config>
      <ipv6 xmlns="urn:ios">
        <unicast-routing/>
      </ipv6>
      </config>
  </device>
  </devices>
</config>
admin@ncs#
```

Then lets look at the xpath representation of the same configuration:
```xls
admin@ncs# show running-config devices device lab-gw0 config ios:ipv6 | display xpath
/devices/device[name='lab-gw0']/config/ios:ipv6/unicast-routing
```

# Step 2 - View in NSO WebUI

Now lets look at this same information in the NSO webUI.

Go to localhost:8080

1. Then select the netsim that you configured.
2. Inside the device, select the config tab
3. Search for the ipv6 link
4. Look for the node (checkmark box) for unicast-routing

Take a moment to look at the breadcrumb right below the top level menu. Compare the structure to our xpath from above.

# Step 3 - Draw out the navigation

On a piece of paper (or a drawing program), draw out the navigation path to our ipv6 unicast-routing command.

Draw this similar to the slides we have seen, in the hierarchy / data tree view.
