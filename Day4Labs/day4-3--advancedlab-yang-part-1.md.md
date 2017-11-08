# ACL Interface Compliance Service Model - YANG

This Lab will go through building a YANG model for the ACL Application Use Case. We will just cover IPv4 for this lab.

## Requirements

The model will capture:
1. Device(s) (Network device that needs the ACL applied)
2. IPv4 ACL Name
3. Interface to have applied to
4. Direction

The end application will use this data to enforce that the entered ACL is in fact on the selected interfaces.
We want to be able to easily add device/interface pairs to a given ACL to have applied.

## High Level Abstraction

For our Model we want to capture the data above, but need to determine our logical groupings.

For example, do we take a Device first approach?
```
    Device
       |
       |
ACL Name, ACL Direction
   |
   |
Interfaces
    |
    |
Int Type, Int Number

```

Or do we take a ACL first approach?
```
      ACL Name, ACL Direction
          |
          |
  Device(s)
      |
      |
  Interfaces
      |
      |
  Int Type, Int Number

```

For this lab we will choose the second schema, as it allows us to easily add new device/interface pairs for a given ACL.

Before we jump into building the YANG lets define and set some restrictions on our attributes.

1. ACL Name (key)
  The ACL Name will be our key as we want unique ACL names and directions.
2. ACL Direction (key)
  The Direction the ACL is applied in. We will key of this as well so that we can have an ACL twice, but in different directions. This will be limited to "in" and "out".
3. Device(s)
  The Networking devices that will have the ACL applied. Should exist in NSO.
4. Interfaces
  The interfaces to have applied to. This should be a list of interfaces specifying the interface type and number.
    1. Interface Type
        Should be limited options to: FastEthernet, GigabitEthernet, TenGigEthernet, Tunnel
    2. Interface Number
        The interface number to be applied to

## Building the Model

Now that we have our data-model and our constraints we are ready to build our YANG Model!

Start by creating a new service package using the NSO make-package tools.

In this portion of the lab we will only generate the YANG. We will tackle the remainder of the package in further labs.

`BRANBLAC-M-W0WN:BGL Training branblac$ ncs-make-package --service-skeleton template acl_lab --augment /ncs:services`

What this command is saying is: Make a new NSO service package based on the NSO Skeleton for a XML template service. The name of the package is 'acl_lab' and it is a service.

This will auto-generate for us the structure for our YANG model! To view the model open the acl_lab.yang file.
The file is located in acl_lab/src/yang/acl_lab.yang

> Note: It is usually best to run this command inside your NSO running directory's packages folder.

We will be modifying the skeleton by adding our model inside the acl_lab list:

```
augment /ncs:services {
list acl_lab {
  key name;
  ...
```

This is saying we will have a list of acl_labs instances (ie ACLs ) that we will add to to configure the network and enforce our ACLs.

Now, lets create a model one attribute at a time.

### ACL Name (key):
Our ACL name will be a string. In the future we may wish to write regexs or limit the length to ensure that only device acceptable ACL names are used. For this lab we will trust our user (Not preferred for production).

```
list acl_lab {
  key ACL_Name;

  leaf ACL_Name {
    type string;
  }
  ...
```

### ACL Direction (key)
The Direction the ACL is applied in. We will key of this as well so that we can have an ACL twice, but in different directions. This will be limited to "in" and "out". We will accomplish this via the enumeration type. We then need to also add the leaf as a key for the list.
```
list acl_lab {
  key "ACL_Name ACL_Direction";

  leaf ACL_Direction {
    type enumeration{
      enum "in";
      enum "out";
    }
  }
  ...
```

### Device(s)
This will be which devices to have the ACL Applied to. This will need to have the ability to nest information below it.

Referring back to our model:

```
  ACL Name, ACL Direction
          |
          |
  Device(s)
      |
      |
  Interfaces
      |
      |
  Int Type, Int Number
```

We will accomplish this via nested lists (yes, lists within lists within lists!, YANG is a Hierarchal Model https://en.wikipedia.org/wiki/Hierarchical_database_model)

This structure will look as such:

```
list devices
    device-name
    list Interfaces
        interface_type, interface_number
```

Now lets put that model into YANG.

The first attribute we need is a reference to the networking device. We can use YANG leafref types to look up devices that are stored in the NSO DB:

```
list devices {
  key device_name;

  leaf device_name {
    type leafref {
      path "/ncs:devices/ncs:device/ncs:name";
    }
  }
}
```

Then, we need to define our interfaces list inside the devices list. Representing a list of interfaces PER device in the devices list. This list will have a key of the interface type & number (ie unique interface):

```
list devices {
  key device_name;

  list interfaces {
    key "interface_type interface_number";

  }
}
```

Now lets define our interface data types. the interface_type should be of specific types. So lets define it with a enumeration. While the Interface number will follow a pattern of `digit` or `digit/digit` or `digit/digit/digit`  (for now we will just use a string, but for production would either do look ups or RegExs).
(We could also do dynamic looks ups of the devices available interfaces but will not in this lab, dynamic lookup would be the production recommended approach)

```
list interfaces {
  key "interface_type interface_number";

  leaf interface_type {
    type enumeration{
      enum "FastEthernet";
      enum "GigabitEthernet";
      enum "TenGigEthernet";
      enum "Tunnel";
    }
  }

  leaf interface_number {
    type string;
  }
}
```

We have now defined our model! the completed model should look something like:

```
module acl_lab {
  namespace "http://com/example/acl_lab";
  prefix acl_lab;

  import ietf-inet-types {
    prefix inet;
  }
  import tailf-ncs {
    prefix ncs;
  }

  augment /ncs:services {
  list acl_lab {
    key "ACL_Name ACL_Direction";
    uses ncs:service-data;
    ncs:servicepoint "acl_lab";

    leaf ACL_Name {
      type string;
    }

    leaf ACL_Direction {
      type enumeration{
        enum "in";
        enum "out";
      }
    }

    list devices {
      key device_name;

      leaf device_name {
        type leafref {
          path "/ncs:devices/ncs:device/ncs:name";
        }
      }
      list interfaces {
        key "interface_type interface_number";

        leaf interface_type {
          type enumeration{
            enum "FastEthernet";
            enum "GigabitEthernet";
            enum "TenGigEthernet";
            enum "Tunnel";
          }
        }

        leaf interface_number {
          type string;
        }
      }
    }

  }
  } // augment /ncs:services {
}
```

Now if we navigate to the folder with the file and run pyang we can check for errors:
```
BRANBLAC-M-W0WN:yang branblac$ pyang acl_lab.yang
acl_lab.yang:5: warning: imported module ietf-inet-types not used
/Users/branblac/ncs-4.4/src/ncs/yang/tailf-ncs-devices.yang:22: warning: imported module tailf-ncs-monitoring not used
/Users/branblac/ncs-4.4/src/ncs/yang/tailf-ncs-devices.yang:1323: error: node tailf-ncs::connect is not found
/Users/branblac/ncs-4.4/src/ncs/yang/tailf-ncs-devices.yang:1333: error: node tailf-ncs::sync-to is not found
/Users/branblac/ncs-4.4/src/ncs/yang/tailf-ncs-devices.yang:1343: error: node tailf-ncs::sync-from is not found
/Users/branblac/ncs-4.4/src/ncs/yang/tailf-ncs-devices.yang:1353: error: node tailf-ncs::disconnect is not found
/Users/branblac/ncs-4.4/src/ncs/yang/tailf-ncs-devices.yang:1363: error: node tailf-ncs::check-sync is not found
/Users/branblac/ncs-4.4/src/ncs/yang/tailf-ncs-devices.yang:1373: error: node tailf-ncs::check-yang-modules is not found
/Users/branblac/ncs-4.4/src/ncs/yang/tailf-ncs-devices.yang:1384: error: node tailf-ncs::fetch-ssh-host-keys is not found
/Users/branblac/ncs-4.4/src/ncs/yang/tailf-ncs-devices.yang:3278: error: node tailf-ncs::disconnect is not found
BRANBLAC-M-W0WN:yang branblac$
```

Now, this may look like we have errors, but we do not! the errors are from the NSO Service modules and will not impact our model. ( the reason for the errors is due to pyang paths not finding the imported modules)

The final step is to compile your YANG/service package.

From the src folder (acl_lab/src) enter the make command. Should should receive no errors:
```bash
BRANBLAC-M-W0WN:src branblac$ make
/Users/branblac/ncs-4.4/bin/ncsc  `ls acl_lab-ann.yang  > /dev/null 2>&1 && echo "-a acl_lab-ann.yang"` \
              -c -o ../load-dir/acl_lab.fxs yang/acl_lab.yang
BRANBLAC-M-W0WN:src branblac$

```

## Summary

In the lab we:
1. Modeled an application for enforcing ACL application
2. Defined the data model and constraints
3. Created an NSO Service Application package
4. Modified the package with our data model for ACL application.

Next labs we will:
1. Generate the mapping template for Modeled
2. Test our package
