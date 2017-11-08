# Day 4 Lab 1 - Usage for simple service

For our first set of labs with services we are going to build the simple service example showing a global radius server design that has different ip addresses per region.

This service package will be pure YANG XML.

It is now time for us to test to ensure our service works as expected.

For our AMER Region, we expecting the config below to be applied to every device in its device list:

```
radius server one
  address ipv4 10.0.0.1 auth-port 1812 acct-port 1813
```

# Step 1

Lets first test that the service can apply to one device.

Enter into config mode from the nso cli:

```
ncs_cli -C -u admin
```

Then create our AMER service instance:

```
branblac@ncs# config
Entering configuration mode terminal
branblac@ncs(config)# services radius_service ?
Possible completions:
  AMER  APJC  EMEA  range
branblac@ncs(config)# services radius_service AMER
branblac@ncs(config-radius_service-AMER)#
```

Now, lets see our configuration options:
```
branblac@ncs(config-radius_service-AMER)# ?
Possible completions:
  check-sync           Check if device config is according to the service
  commit-queue         
  deep-check-sync      Check if device config is according to the service
  device               
  get-modifications    Get the data this service created
  ip-address           
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
  rload                Load configuration from an ASCII file relative to
                       current location
  top                  Exit to top level and optionally run command
  ```

Lets start by setting the ip-address for our AMER region

```
branblac@ncs(config-radius_service-AMER)# ip-address ?
Possible completions:
  <IPv4 address>
branblac@ncs(config-radius_service-AMER)# ip-address 10.0.0.1
branblac@ncs(config-radius_service-AMER)#
```

We are now ready to add devices to our AMER radius server:
```
branblac@ncs(config-radius_service-AMER)# device ?
Possible completions:
  [  mydevice
branblac@ncs(config-radius_service-AMER)# device mydevice
```

Now lets check what is going to be configured:
```
admin@ncs(config-radius_service-AMER)# commit dry-run
cli {
    local-node {
        data  devices {
                  device mydevice {
                      config {
                          ios:radius {
             +                server one {
             +                    address {
             +                        ipv4 {
             +                            host 10.0.0.1;
             +                            auth-port 1812;
             +                            acct-port 1813;
             +                        }
             +                    }
             +                }
                          }
                      }
                  }
              }
              services {
             +    radius_service AMER {
             +        device [ mydevice ];
             +        ip-address 10.0.0.1;
             +    }
              }
    }
}
admin@ncs(config-radius_service-AMER)#
```

and also in the native Cisco CLI:

```admin@ncs(config-radius_service-AMER)# commit dry-run outformat native
native {
    device {
        name mydevice
        data radius server one
              address ipv4 10.0.0.1 auth-port 1812 acct-port 1813
             !
    }
}
```

And as we can see the service is configuring as expected.

Now you try configuring the other regions and devices.

# Step 2

Now lets test the Service compliance functionality.  

Commit the changes from above to save the radius records into the data base.

Then, for the given device lets change our radius one configuration.

```
dmin@ncs(config)# devices device mydevice config ios:radius server one
admin@ncs(config-server-one)# address ipv4 1.1.1.1 acct-port 10 au
                                                                ^
% Invalid input detected at '^' marker.
admin@ncs(config-server-one)# address ipv4 1.1.1.1 acct-port 10 ?
Possible completions:
  <cr>
admin@ncs(config-server-one)# address ipv4 1.1.1.1 acct-port 10
```

We are now ready to check our servive for compliance:

```
admin@ncs(config)# services radius_service AMER check-sync
in-sync false
```

NSO is now telling us something is wrong with our AMER radius configuration. but what?

Use outformat native to find out what:

```
admin@ncs(config)# services radius_service AMER check-sync outformat native
native {
    device {
        name mydevice
        data
              radius server one
               address ipv4 10.0.0.1 auth-port 1812 acct-port 1813
              !

    }
}
```

# Step 3

Now that we have a mis-configuration in our network, lets use NSO to remediate it.

From our service, lets issue a re-deploy to remediate our configuration.

But first, lets try a dry-run outformat native to see what will be sent to remediate the network.

```
admin@ncs(config-radius_service-AMER)# re-deploy dry-run { outformat native }
native {
    device {
        name mydevice
        data
              radius server one
               address ipv4 10.0.0.1 auth-port 1812 acct-port 1813
              !

    }
}
```

Lets now use NSO to correct the issue:

```
admin@ncs(config-radius_service-AMER)# re-deploy                             
admin@ncs(config-radius_service-AMER)#
```

Now that NSO has correct the compliance issue, lets validate that out service is in sycn:
```
admin@ncs(config-radius_service-AMER)# check-sync
in-sync true
```
