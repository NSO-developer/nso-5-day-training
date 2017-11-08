# ACL Interface Compliance Service Model - Testing and Usage

Now that we have built our YANG, XML, and have loaded the package into NSO we our ready to test and use our package.


## Testing

There are several methods to use for testing our application, from programatic like LUX or Python Unittests to manual user testing.

For the scope of this lab, we will just be testing via user usage.

Lets go ahead and test via the NSO CLI

1. Enter the CLI: `ncs_cli -C -u admin`
2. Enter Config Mode `conf`
3. View our existing / options for creating a new service `servces acl_lab ?`
  ```
  admin@ncs(config)# services acl_lab ?
Possible completions:
  <ACL_Name:string>  range
  ```
  This tells us to enter in a string for our ACL_Name
4. Create a new service `services acl_lab test_acl ?`
```
admin@ncs(config)# services acl_lab test_acl ?
Possible completions:
in  out
```
Then choice the direction of the ACL `services acl_lab test_acl in` -> press enter
5. Now, enter a new device to have the ACL (the ? will show devices in your NSO)
```
admin@ncs(config-acl_lab-test_acl/in)# devices ?
Possible completions:
  customer-gw0  customer-gw1  lab-gw0  lab-gw1  range  svl-gem-lab-gw1
admin@ncs(config-acl_lab-test_acl/in)# devices customer-gw1
```
6. Now enter in the interface information (for now we will do 1 interface, then test multiple):
```
admin@ncs(config-acl_lab-test_acl/in)# devices customer-gw1 ?
Possible completions:
  interfaces  <cr>
admin@ncs(config-acl_lab-test_acl/in)# devices customer-gw1 interfaces ?
Possible completions:
  FastEthernet  GigabitEthernet  TenGigEthernet  Tunnel
  admin@ncs(config-acl_lab-test_acl/in)# devices customer-gw1 interfaces Tunnel ?
Possible completions:
  <interface_number:string>
admin@ncs(config-acl_lab-test_acl/in)# devices customer-gw1 interfaces Tunnel 2
```

Once the information is entered, we can test if the end CLI is as expected using the commit dry-run outformat native functionality.

This will run our application logic and tell us what will be pushed down to the device before NSO actually sends it. this way, we can see and validate the config prior to pushing.

```
admin@ncs(config-interfaces-Tunnel/2)# commit dry-run outformat native
native {
    device {
        name customer-gw1
        data interface Tunnel2
              ip access-group test_acl in
              no shutdown
             exit
    }
}
```

The info after 'data', is the CLI commands NSO will send down to the device.

Now, lets add an interface to validate ur interface loop.

```
admin@ncs(config-interfaces-Tunnel/2)# exit
admin@ncs(config-devices-customer-gw1)# ?
Possible completions:
  interfaces   
  ---          
  commit       Commit current set of changes
  describe     Display transparent command information
  exit         Exit from current mode
  help         Provide help information
  no           Negate a command or set its defaults
  pwd          Display current mode path
  rload        Load configuration from an ASCII file relative to current location
  top          Exit to top level and optionally run command
admin@ncs(config-devices-customer-gw1)# interfaces FastEthernet 2
```

And the outputted CLI:

```
admin@ncs(config-interfaces-FastEthernet/2)# commit dry-run outformat native
native {
    device {
        name customer-gw1
        data interface Tunnel2
              ip access-group test_acl in
              no shutdown
             exit
             interface FastEthernet2
              no switchport
              ip access-group test_acl in
              no shutdown
             exit
    }
}
```

From here we can see that the interface loop and if/when statements are working properly. So now, lets add a device and interface to validate that the device loop is working.

```
admin@ncs(config-interfaces-FastEthernet/2)# exit
admin@ncs(config-devices-customer-gw1)# exit
admin@ncs(config-acl_lab-test_acl/in)# devices lab-gw0
admin@ncs(config-devices-lab-gw0)# interfaces T
Possible completions:
  TenGigEthernet  Tunnel
admin@ncs(config-devices-lab-gw0)# interfaces Tunnel 3
```

and the outputted CLI:
```
admin@ncs(config-interfaces-Tunnel/3)# commit dry-run outformat native
native {
    device {
        name customer-gw1
        data interface Tunnel2
              ip access-group test_acl in
              no shutdown
             exit
             interface FastEthernet2
              no switchport
              ip access-group test_acl in
              no shutdown
             exit
    }
    device {
        name lab-gw0
        data interface Tunnel3
              ip access-group test_acl in
              no shutdown
             exit
    }
}
```


Great! all loops and if/when statements are working as expected.

We have thus successfully developed an application for adding and tracking an ACLs application across many interfaces across many devices, and tested/validated that the config pushed is correct.

Finally, either start a new config or use the one we entered above and fully commit the chagnes to the network: `commit`. This will save the config changes into the NSO database and send the config down to the network device.

Next, we will see how NSO can then manage the full lifecycle of the configuration. After all, just generating CLI from a template isn't that hard to do!

## Usage

Now that we have a working application in NSO, lets use it.

The cool thing with NSO is that we now have a database that stores information about the network. Since our package has a list of ACLs that it manages, we can actually use NSO to view the list of ACL it manages:

From the CLI:

```
admin@ncs# services acl_lab ?
Possible completions:
  test_acl
```

We can also view this same information in the WebUI or via REST APIs (and Java/ Python!)

WEbUI Link:  http://localhost:8080/index.html#/model/ncs:services/acl_lab:acl_lab
REST API EndPoint: http://localhost:8080/api/running/services/acl_lab

Then we can see all the devices and interfaces that the ACL in a direction has been applied to:

```
admin@ncs# show running-config services acl_lab test_acl in devices
services acl_lab test_acl in
 devices customer-gw1
  interfaces FastEthernet 2
  !
  interfaces Tunnel 2
  !
 !
 devices lab-gw0
  interfaces Tunnel 3
  !
 !
!
```

We can also navigate this through he WebUI and parse this from the REST API XML or JSON.

## Compliance Checking

Now,  lets see how NSO can easily be used to conduct compliance checks for missing ACL application.

Since we now have a database that specifies which devices, on which interface are suppose to have which ACL, we can use this to run a comparison against the device configuration its self and flag deltas.

NSO calls this action a 'check-sync' since it is checking if the device is in-sync with what our model says it should be.

Lets have some fun, by breaking security policy and removing the ACLs we just applied.

In NSO, either through the CLI, WebUI, or even REST remove one one of the configured ACLs

Example in CLI:

```
admin@ncs(config)# no devices device lab-gw0 config ios:interface Tunnel 3 ip access-group test_acl in
admin@ncs(config)# commit
Commit complete.
```

Now, lets run a 'check-sync' on the instance for 'test_acl in'

from the NSO CLI global mode:
```
admin@ncs# services acl_lab test_acl in check-sync
in-sync false
admin@ncs#
```

As we can see, NSO has found out that something is not in-sync! In otherwords, the ACL is missing on an interface somewhere.

But where? Let NSO tell us:

```
admin@ncs# services acl_lab test_acl in check-sync outformat native
native {
    device {
        name lab-gw0
        data
              interface Tunnel3
               ip access-group test_acl in
              exit

    }
}
```

We can now see, in Cisco CLI, that the ACL is missing from interface Tunnel3, along with the CLI commands NSO would issue to make this service compliant.

Great! Now lets resolve the Compliance issue with one command.

```
admin@ncs# services acl_lab test_acl in re-deploy
admin@ncs#
admin@ncs# services acl_lab test_acl in check-sync                 
in-sync true
```

And just like that our device is reconfigured with the correct ACL, in the correct direction, on the correct interface.

> Note, for large applications to many devices it is best to use commit queues `admin@ncs# services acl_lab test_acl in re-deploy commit-queue `


## Decommissioning

So far we covered the creation and compliance aspects of configuration lifecycle, we are now ready to see how NSO can handle the decommissioning of our ACL configuration.

We can decommission our dummy ACL at all levels with ease:
1. Remove ACL (in a direction) from an interface
2. Remove ACL (in a direction) from all of a devices interfaces
3. Remove ACL (in a direction) from all interfaces of all devices

To remove the ACL from a single interface:
Enter into NSO config mode `config`

```
admin@ncs(config)# no services acl_lab test_acl in devices lab-gw0 interfaces Tunnel 3
admin@ncs(config)# commit dry-run outformat native
native {
    device {
        name lab-gw0
        data interface Tunnel3
              no ip access-group test_acl in
              no shutdown
             exit
             no interface Tunnel3
    }
}
```

We can see, NSO then removes that ACL (in a direction) from the device and the database.

Then to remove an ACL from a device:
```
admin@ncs(config)# no services acl_lab test_acl in devices customer-gw1
admin@ncs(config)# commit dry-run outformat native                     
native {
    device {
        name customer-gw1
        data interface Tunnel2
              no ip access-group test_acl in
              no shutdown
             exit
             no interface Tunnel2
             no interface FastEthernet2
    }
}
```

As we can see, it removes for all interfaces on that device.

And finally if we want to remove an ACL (in a direction) entirely from all devices:

```
admin@ncs(config)# no services acl_lab test_acl in                     
admin@ncs(config)# commit dry-run outformat native
native {
    device {
        name customer-gw1
        data interface Tunnel2
              no ip access-group test_acl in
              no shutdown
             exit
             no interface Tunnel2
             no interface FastEthernet2
    }
    device {
        name lab-gw0
        data interface Tunnel3
              no ip access-group test_acl in
              no shutdown
             exit
             no interface Tunnel3
    }
}
```

## Recap

In Summary, with minimal code (in fact, no 'real' code at all!) we have created a functioning application managing the application ACLs to interfaces.

This app can:
1. create, audit and remove ACLs across devices, multiple interfaces or a single interface.
2. Report on where we have what ACL applied in what direction
3. Intelligently audit for mis-applied ACLs.
