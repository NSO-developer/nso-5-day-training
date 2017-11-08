# Day 4 Lab 1 - Yang for simple service

For our first set of labs with services we are going to build the simple service example showing a global radius server design that has different ip addresses per region.

This service package will be pure YANG XML.

Our YANG Model will have the following attributes:

1. IP address of the regional server
2. Unique name of the region
3. List of devices that are to be configured with the server


# Step 1

Begin by creating a new NSO Service package in the ncs-run directory:
```
BRANBLAC-M-W0WN:BGL Training branblac$ ncs-make-package --service-skeleton template radius_service --augment /ncs:services
```

# Step 2

Open the radius_service/src/yang/radius_service.yang file.

```yang
module radius_service {
  namespace "http://com/example/radius_service";
  prefix radius_service;

  import ietf-inet-types {
    prefix inet;
  }
  import tailf-ncs {
    prefix ncs;
  }

  augment /ncs:services {
  list radius_service {
    key name;

    uses ncs:service-data;
    ncs:servicepoint "radius_service";

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
  } // augment /ncs:services {
}

```

# Step 3

Lets start by setting up the region name en enforce its unique.

To do this, we want to leverage the region name as the key for our list of services. This means that every new instance must have a unique name. Then we want to ensure there is only the permitted region names.

We can ensure the permitted region names through an enumeration type:

```
leaf Region {
  type enumeration {
    enum "AMER";
    enum "APJC";
    enum "EMEA";
  }
}
```

Now lets set our new leaf as the key:
```
module radius_service {
  namespace "http://com/example/radius_service";
  prefix radius_service;

  import ietf-inet-types {
    prefix inet;
  }
  import tailf-ncs {
    prefix ncs;
  }

  augment /ncs:services {
  list radius_service {
    key Region;

    leaf Region {
      type enumeration {
        enum "AMER";
        enum "APJC";
        enum "EMEA";
      }
    }
...
```

Now, we need to add a leaf for the server ip address. we want to ensure it is an ipv4 address as well:

```yang
leaf ip-address {
  type inet:ipv4-address;
}
```

Luckily, the skeleton pre-comes with a list of devices for us:
```
leaf-list device {
  type leafref {
    path "/ncs:devices/ncs:device/ncs:name";
  }
}
```

We should also now remove the name & dummy leafs that the skeleton created.

Our completed YANG should look similar to:

```yang
module radius_service {
  namespace "http://com/example/radius_service";
  prefix radius_service;

  import ietf-inet-types {
    prefix inet;
  }
  import tailf-ncs {
    prefix ncs;
  }

  augment /ncs:services {
  list radius_service {
    key Region;

    leaf Region {
      type enumeration {
        enum "AMER";
        enum "APJC";
        enum "EMEA";
      }
    }

    uses ncs:service-data;
    ncs:servicepoint "radius_service";

    // may replace this with other ways of refering to the devices.
    leaf-list device {
      type leafref {
        path "/ncs:devices/ncs:device/ncs:name";
      }
    }

    leaf ip-address {
      type inet:ipv4-address;
    }
  }
  } // augment /ncs:services {
}
```

# Step 4

Now that our YANG model is complete we can compile the model.

cd to our packages src directory and type make:

```cli
BRANBLAC-M-W0WN:packages branblac$ cd radius_service/src
BRANBLAC-M-W0WN:src branblac$ make
mkdir -p ../load-dir
/Users/branblac/ncs-4.4/bin/ncsc  `ls radius_service-ann.yang  > /dev/null 2>&1 && echo "-a radius_service-ann.yang"` \
              -c -o ../load-dir/radius_service.fxs yang/radius_service.yang
```
