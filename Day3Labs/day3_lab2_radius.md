# Building a simple service

For this lab we will be creating a simple service to configure a global Radius server configuration.

This lab will be able to configure and enforce a global radius server configuration across many devices.

The config we will be sending is:
```
radius server one
  address ipv4 (our ip address) auth-port 1812 acct-port 1813
```

# Step 1

Our first step is to create a new nso package.

navigate to your ncs-run/packages directory and type:

`ncs-make-package --service-skeleton template simple_radius --augment /ncs:services`

This will create an new nso package for us.

# Step 2

Our second step is to configure the YANG Service model with the our needed input parameters.

Open the simple_radius.yang file that is found in  ncs-run/packages/simple_radius/src/yang

Inside the list:
```
list simple_radius {
...
}
```

Change the name node to represent our radius server ip address, update the key, and remove the dummy node:

```
list simple_radius {
    key radius_server_ip;

    uses ncs:service-data;
    ncs:servicepoint "simple_radius";

    leaf radius_server_ip {
      type inet:ipv4-address;
    }

    // may replace this with other ways of refering to the devices.
    leaf-list device {
      type leafref {
        path "/ncs:devices/ncs:device/ncs:name";
      }
    }

```

We are now complete with our model and ready to compile/make our package for NSO.

In side the ncs-run/packages/simple_radius/src/  folder type `make`

The results should look as below:
```
BRANBLAC-M-W0WN:src branblac$ make
/Users/branblac/ncs-4.4/bin/ncsc  `ls simple_radius-ann.yang  > /dev/null 2>&1 && echo "-a simple_radius-ann.yang"` \
              -c -o ../load-dir/simple_radius.fxs yang/simple_radius.yang
```

# Step 3

Now we need to build our XML template.

First we need to get the XML structure for our template.

Begin by configuring a device with the needed config in the nso cli, then iss `commit dry-run outformat xml`

```
admin@ncs# conf
Entering configuration mode terminal
admin@ncs(config)# devices device netsim_lab_gw config
admin@ncs(config-config)# ios:radius server one
admin@ncs(config-server-one)# address ipv4 10.0.0.1 auth-port 1812 acct-port 1813
admin@ncs(config-server-one)# commit dry-run outformat xml
result-xml {
    local-node {
        data <devices xmlns="http://tail-f.com/ns/ncs">
               <device>
                 <name>netsim_lab_gw</name>
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
admin@ncs(config-server-one)# end
Uncommitted changes found, commit them? [yes/no/CANCEL] no
```
Now, open the xml file inside ncs-run/packages/simple_radius/templates

It should look like:

```xml
<config-template xmlns="http://tail-f.com/ns/config/1.0"
                 servicepoint="simple_radius">
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

We now have the basic structure for our template. Copy the tags from our dry-run <config> to </config>  into the templates <config> to </config>:

```xml
<config-template xmlns="http://tail-f.com/ns/config/1.0"
                 servicepoint="simple_radius">
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

Great! Now we just need to chagne the ip address for the server to our inputed YANG variable.

Do this via the {/variable_name} form, for us it would be {/radius_server_ip}

```xml
<config-template xmlns="http://tail-f.com/ns/config/1.0"
                 servicepoint="simple_radius">
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
        <radius xmlns="urn:ios">
          <server>
            <id>one</id>
            <address>
              <ipv4>
                <host>{/radius_server_ip}</host>
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

# Step 4

Great, were have now completed our development phase!

Lets load the package into our NSO and test it.

From the nso cli issue the packages reload command:

```
admin@ncs# packages reload

>>> System upgrade is starting.
>>> Sessions in configure mode must exit to operational mode.
>>> No configuration changes can be performed until upgrade has completed.

reload-result {
    package simple_radius
    result true
}
```

# Step 5

Now test your service!

From the webUI or CLI:

Create an instance of your service service, add a device or many and issue a commit dry-run outformat native.

You should see:
```
radius server one
 address ipv4 10.0.0.3 auth-port 1812 acct-port 1813
!
```

but with your inputted ip address!

# Step 6

Think about our model.

What might go wrong with it? What if we want more than one server?

How many you improve this model?
