# Creating an Yang Module using NSO Bash commands

You can have NSO auto generate a yang module for you. By default, it plugs in some service data information to the service skeleton, but for our simple example we are going to remove it.

# Creating the Service Skeleton and adapting it to be a simple module

```
cd ncs-run
cd packages
ncs-make-package --service-skeleton template bgl-test
rm bgl-test/templates/bgl-test-template.xml
```

We just created a yang module called bgl-test and removed the xml template to simplify things.

By default the yang module looks like this:
```
module bgl-test {
  namespace "http://com/example/bgltest";
  prefix bgl-test;

  import ietf-inet-types {
    prefix inet;
  }
  import tailf-ncs {
    prefix ncs;
  }

  list bgl-test {
    key name;

    uses ncs:service-data;
    ncs:servicepoint "bgl-test";

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
}
```

Do not worry about all the service stuff for now, just wipe out the file and replace it (with same filename), with this information:

```
module bgl-test {
  namespace "http://com/example/bgltest";
  prefix bgl-test;

  container my_tab_around_this{
    leaf a_yang_input {
      type string;
    }
  }
}
```

In this most simple example, we are creating a container to house a single piece of information, stored as a string. Since this is not importing anything else, or dealing with any Cisco config, it is a simple standalone module that will be accessible at the NSO root hierarchy.

# Integrating the simple yang module into NSO

## Make the yang

*note* that when you are updating yang modules for NSO you need to do *both* a bash "make" command in the src folder in that package directory *and* a packages reload within the NSO application. For example:

```
cd ncs-run/packages/bgl-test/src
make
```

and you should get a result like this:

```
mkdir -p ../load-dir
mkdir -p java/src
/Users/jabelk/ncs-all/ncs-4.4/bin/ncsc  `ls bgl-test-ann.yang  > /dev/null 2>&1 && echo "-a bgl-test-ann.yang"` \
              -c -o ../load-dir/bgl-test.fxs yang/bgl-test.yang
```

This is completely normal. If you have any critical errors it would show here, like this:

```
/Users/jabelk/ncs-all/ncs-4.4/bin/ncsc  `ls bgl-test-ann.yang  > /dev/null 2>&1 && echo "-a bgl-test-ann.yang"` \
              -c -o ../load-dir/bgl-test.fxs yang/bgl-test.yang
yang/bgl-test.yang:11:3: error: trailing garbage after module
make: *** [../load-dir/bgl-test.fxs] Error 1
```

Trailing garbage usually means you forgot a semi colon or a closing {}. Use Atom/Sublime or pyang to help with that.

## Reload the packages

Now login to the NSO CLI:
```
ncs_cli -C -u admin
packages reload
```

The packages reload may take a bit, so be patient. It should look like this:

```
dmin@ncs# packages reload

>>> System upgrade is starting.
>>> Sessions in configure mode must exit to operational mode.
>>> No configuration changes can be performed until upgrade has completed.
>>> System upgrade has completed successfully.
reload-result {
    package bgl-test
    result true
}
reload-result {
    package bgl-test2
    result false
    info [bgl-test2-template.xml:2 Unknown servicepoint: bgl-test2]
}
reload-result {
    package cisco-ios
    result true
}
```

Note I have another packages above (bgl-test2) in which I purposely left in some additional errors to show what it would look like to fail on a packages reload.
To fix this, I would need to fix my yang syntax and run another make, then run another package reload.

# Validating the module and using it

Now that I have this simple module loaded into NSO I can access it through the Web GUI/CLI/Rest API/Python API etc.

```
admin@ncs(config)# my_tab_around_this ?
Possible completions:
  a_yang_input
admin@ncs(config)# my_tab_around_this a_yang_input "I love chocolate"
admin@ncs(config)# commit dry-run
cli {
    local-node {
        data  my_tab_around_this {
             +    a_yang_input "I love chocolate";
              }
    }
}
admin@ncs(config)#
```

Try finding it on the web GUI as well (hint go to the top left three horizontal lines and click to get root menu) and look for the container:
```
Modules
▼bgl-test
  my_tab_around_this
```

click on my_tab_around_this and you should see the value you created from the CLI. Now update it through the GUI, and click Commit.

# Taking it to the next level
Now you try implementing some other yang inputs in the above module, re-make the yang, re-load the packages and see the result.

Pick something simple, like adding some more leaf's or maybe some nested containers. Maybe use your inputs from yesterday's service pen and paper yang excercise? Or some cricket team inputs?
