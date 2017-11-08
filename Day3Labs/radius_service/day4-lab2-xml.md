# Day 4 Lab 1 - XML for simple service

For our first set of labs with services we are going to build the simple service example showing a global radius server design that has different ip addresses per region.

This service package will be pure YANG XML.

Our service will apply the configuration:

```
radius server one
  address ipv4 10.0.0.1 auth-port 1812 acct-port 1813
```

We ip addresses varying on which region we are in.

# Step 1

Begin by entering the NSO CLI
```
BRANBLAC-M-W0WN:BGL Training branblac$ ncs_cli -C -u admin
```

Then enter into config mode and begin configuring a netsim or ios device for the above cli:

```
BRANBLAC-M-W0WN:src branblac$ ncs_cli -C -u admin

admin connected from 127.0.0.1 using console on BRANBLAC-M-W0WN
admin@ncs# config
Entering configuration mode terminal
admin@ncs(config)# devices device lab-gw0 config
admin@ncs(config-config)# ios:radius server one
admin@ncs(config-server-one)# address ipv4 10.0.0.1 a
Possible completions:
  acct-port   UDP port for RADIUS accounting server (default is 1646)
  auth-port   UDP port for RADIUS authentication server (default is 1645)
admin@ncs(config-server-one)# address ipv4 10.0.0.1 auth-port 1812 acct-port 1813
```

Once configured, issue a commit dry-run outformat xml command to get our xml skeleton:
```xml
admin@ncs(config-server-one)# commit dry-run outformat xml
result-xml {
    local-node {
        data <devices xmlns="http://tail-f.com/ns/ncs">
               <device>
                 <name>lab-gw0</name>
                 <config>
                   <radius xmlns="urn:ios">
                     <server>
                       <id>one</id>
                       <address>
                         <ipv4>
                           <host>10.0.0.1</host>
                           <auth-port>1812</auth-port>
                           <acct-port>1813</acct-port>
                         </ipv4>
                       </address>
                     </server>
                   </radius>
                 </config>
               </device>
             </devices>
    }
}
```

# Step 2

Now that we have our base template lets put it into our services XML template.

Open the file in the packages templates directory:

```xml
<config-template xmlns="http://tail-f.com/ns/config/1.0"
                 servicepoint="radius_service">
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

Now, lets place the config tags from out outputted XML into the template:

```xml
<config-template xmlns="http://tail-f.com/ns/config/1.0"
                 servicepoint="radius_service">
  <devices xmlns="http://tail-f.com/ns/ncs">
    <device>
      <!--
          Select the devices from some data structure in the service
          model. In this skeleton the devices are specified in a leaf-list.
          Select all devices in that leaf-list:
      -->
      <name>{/device}</name>
      <config>
        <radius xmlns="urn:ios">
          <server>
            <id>one</id>
            <address>
              <ipv4>
                <host>10.0.0.1</host>
                <auth-port>1812</auth-port>
                <acct-port>1813</acct-port>
              </ipv4>
            </address>
          </server>
        </radius>
      </config>
    </device>
  </devices>
</config-template>
```

Now, lets replace the ip address with a variable referencing our YANG model:

```xml
<config-template xmlns="http://tail-f.com/ns/config/1.0"
                 servicepoint="radius_service">
  <devices xmlns="http://tail-f.com/ns/ncs">
    <device>
      <!--
          Select the devices from some data structure in the service
          model. In this skeleton the devices are specified in a leaf-list.
          Select all devices in that leaf-list:
      -->
      <name>{/device}</name>
      <config>
        <radius xmlns="urn:ios">
          <server>
            <id>one</id>
            <address>
              <ipv4>
                <host>{/ip-address}</host>
                <auth-port>1812</auth-port>
                <acct-port>1813</acct-port>
              </ipv4>
            </address>
          </server>
        </radius>
      </config>
    </device>
  </devices>
</config-template>
```


# Step 3

Now that our templates complete lets reload our package and see if the template is valid:

```
branblac@ncs# packages reload

>>> System upgrade is starting.
>>> Sessions in configure mode must exit to operational mode.
>>> No configuration changes can be performed until upgrade has completed.
>>> System upgrade has completed successfully.
reload-result {
    package cisco-asa
    result true
}
reload-result {
    package cisco-ios
    result true
}
reload-result {
    package radius_service
    result true
}
reload-result {
    package ubvpn
    result true
}
branblac@ncs#
System message at 2017-10-20 17:44:18...
    Subsystem stopped: ncs-dp-2-cisco-ios:IOSDp
branblac@ncs#
System message at 2017-10-20 17:44:18...
    Subsystem stopped: ncs-dp-1-cisco-asa:ASADp

System message at 2017-10-20 17:44:18...
    Subsystem started: ncs-dp-3-cisco-asa:ASADp
branblac@ncs# branblac@ncs#
System message at 2017-10-20 17:44:18...
    Subsystem started: ncs-dp-4-cisco-ios:IOSDp
```

As we can see, our package has reloaded successfully!
```
reload-result {
    package radius_service
    result true
}
```

Next we will test the package and see how it works.
