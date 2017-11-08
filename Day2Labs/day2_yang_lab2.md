# Introduction to YANG Lab

In this Lab, we will be modeling Switches into a structured data model using YANG.

For a reference to YANG data-types check out the RFC! https://tools.ietf.org/html/rfc6020

## High Level Abstraction

Before we jump into YANG lets take a quick look at what we will be modeling.

At a high level all (or most) switches share a certain number of traits and are unique to their PID. Wee call the Unique item the 'Key'

Things like:
1. Manufacturer
2. Model Number / PID (Key)
3. Platform Series
5. Interfaces
  1. Interface Type
  2. Number of Interfaces
6. MSRP

Our Model now looks like the below:
```
    Switches
      |
      |
      |
Man, PID, Platform Series, Int Type, MSRP
                              |
                              |
                          Type, Number
```

We could keep adding, but this will be good for now.

We now have a rough outline of our data model! We want to enable a schema that allows for a list of switches and each switch will have each of the attributes we described above!

Before we jump into building the YANG lets set some restrictions on our attributes.

1. Manufacturer
  For manufacturer we are going to assume there is a limited number available. For our lab, lets keep it to the main companies. We only want to allow Cisco, Juniper, Arista, and HP (Feel free to add your own)
2. Model Number / PID
  We could look up and determine a repeatable pattern for Cisco PID, however they may vary between manufacturers, as a result we will say this is a "string" or open text
3. Platform Series
  We could -pre-populate manufacture dependent series, but for the exercise will define this as a "string"
4. Interface Type
  For Interface-Type we only want to allow a select number of options FastEthernet, GigabitEthernet, TenGigEthernet etc..
5. Number of Interfaces
  We want to limit the maximum number of interfaces available per switch.
6. MSRP
  We only want to allow integers/numbers for our MSRP / Price data



## Building the Model

Now that we have our data-model and our constraints we are ready to build our YANG Model!

Start by creating a new file called `switches.yang`

Now, open the file in your favorite text editor (Ours is Atom with the YANG Syntax Highlighting).

Now, lets create a model one attribute at a time.

Since this model is standalone, we need to add module definitions for it to compile as a YANG model:

```
module switches {
  namespace "http://example.com/switches";
  prefix switches;

}
```

The first item to create is the list that will contain our switches. Place this inside the module brackets:
```

list Switches {
  key Model_Number;
}

```

This Defines a List data-type in our model where the unique item/ key is the Model_Number attribute.

Next, lets create the Manufacturers. If we remember we want to limit the options to only a select few. In YANG we accomplish this through the enumeration data-type.
```
leaf Manufacturer {
  type enumeration {
    enum 'Cisco';
    enum 'Juniper';
    enum 'Arista';
    enum 'HP';
  }
}
```

Now lets create our key, the Model_Number as a string:
```
leaf Model_Number {
  type string;
}
```

Platform Series as a string:
```
leaf Platform_Series {
  type string;
}
```

Interfaces:
Now we have our Interfaces. The Interfaces may be of multiple types and different number of ports per type. as a result we want a list that allows us to capture these together in one area and enforce we only have 1 record for each type.

Then, for the records we want to add constraints.
```
list Interfaces {
  key Interface_Type;

  leaf Interface_Type {
    type enumeration {
      enum 'FastEthernet';
      enum 'GigabitEthernet';
      enum 'TenGigEthernet';
    }
  }

  leaf Number_of_Interfaces{
    type int64 {
    range "0 .. 48";
    }
  }
}
```

Finally we have the MSRP! and we want this to only be an integer.

```
leaf MSRP {
  type int64;
}
```

Now, our final YANG Model looks like the below:
```
module switches {
  namespace "http://example.com/switches";
  prefix switches;

    list Switches {

      key Model_Number;

      leaf Manufacturer {
        type enumeration {
          enum 'Cisco';
          enum 'Juniper';
          enum 'Arista';
          enum 'HP';
        }
      }

      leaf Model_Number {
        type string;
      }

      leaf Platform_Series {
        type string;
      }

      list Interfaces {
        key Interface_Type;

        leaf Interface_Type {
          type enumeration {
            enum 'FastEthernet';
            enum 'GigabitEthernet';
            enum 'TenGigEthernet';
          }
        }

        leaf Number_of_Interfaces{
          type int64 {
          range "0 .. 48";
          }
        }
      }

      leaf MSRP {
        type int64;
      }

    }
}
```

Congratulations! You just built your first YANG Model which transforms switches into a structured data type!

To validate your model, you can use the pyang tool https://github.com/mbj4668/pyang lucky for you, it comes installed with nso.

From the directory that you created the file, type `pyang switches.yang` If you model is error free then there will be no return!

```
BRANBLAC-M-W0WN:BGL Training branblac$ pyang switches.yang
BRANBLAC-M-W0WN:BGL Training branblac$
```

In recap we:
1. Abstracted Switches into a data model
2. Defined constraints and types for the data model
3. Defined the data model in YANG

## Improving the Model (Optional)

Also, pyang can help us in building YANG models

```
BRANBLAC-M-W0WN:BGL Training branblac$ pyang --help
Usage: pyang [options] [<filename>...]

Validates the YANG module in <filename> (or stdin), and all its dependencies.

Options:
  -h, --help            Show this help message and exit
  -v, --version         Show version number and exit
  -V, --verbose         
  -e, --list-errors     Print a listing of all error and warning codes and
                        exit.
  --print-error-code    On errors, print the error code instead of the error
                        message.
  -W WARNING            If WARNING is 'error', treat all warnings as errors,
                        except any listed WARNING. If WARNING is 'none', do
                        not report any warnings.
  -E WARNING            Treat each WARNING as an error.  For a list of
                        warnings, use --list-errors.
  --ignore-errors       Ignore all errors.  Use with care.
  --canonical           Validate the module(s) according to the canonical YANG
                        order.
  --max-line-length=MAX_LINE_LEN
  --max-identifier-length=MAX_IDENTIFIER_LEN
  -f FORMAT, --format=FORMAT
                        Convert to FORMAT.  Supported formats are: dsdl,
                        depend, name, omni, yin, tree, jstree, capability,
                        yang, uml, jtox, jsonxsl, sample-xml-skeleton
  -o OUTFILE, --output=OUTFILE
                        Write the output to OUTFILE instead of stdout.
  -F FEATURES, --features=FEATURES
                        Features to support, default all.
                        <modname>:[<feature>,]*
  --deviation-module=DEVIATION
                        Deviation module
  -p PATH, --path=PATH  :-separated search path for yin and yang modules
  --plugindir=PLUGINDIR
                        Load pyang plugins from PLUGINDIR
  --strict              Force strict YANG compliance.
  --lax-xpath-checks    Lax check of XPath expressions.
  --trim-yin            In YIN input modules, trim whitespace in textual
                        arguments.
  -L, --hello           Filename of a server's hello message is given instead
                        of module filename(s).
  --keep-comments       Pyang will not discard comments;
                        has effect if the output plugin can
                        handle comments.
  --check-update-from=OLDMODULE
                        Verify that upgrade from OLDMODULE follows RFC 6020
                        rules.
  -P OLD_PATH, --check-update-from-path=OLD_PATH
                        :-separated search path for yin and yang modules used
                        by OLDMODULE
  --ietf                Validate the module(s) according to IETF rules.
  --lint                Validate the module(s) according to RFC 6087 rules.
  --lint-namespace-prefix=LINT_NAMESPACE_PREFIXES
                        Validate that the module's namespace matches one of
                        the given prefixes.
  --lint-modulename-prefix=LINT_MODULENAME_PREFIXES
                        Validate that the module's name matches one of the
                        given prefixes.

  YANG output specific options:
    --yang-canonical    Print in canonical order
    --yang-remove-unused-imports

  YIN output specific options:
    --yin-canonical     Print in canonical order
    --yin-pretty-strings
                        Pretty print strings

  Hybrid DSDL schema output specific options:
    --dsdl-no-documentation
                        No output of DTD compatibility documentation
                        annotations
    --dsdl-no-dublin-core
                        No output of Dublin Core metadata annotations
    --dsdl-record-defs  Record all top-level defs (even if not used)

  Capability output specific options:
    --capability-entity
                        Write ampersands as XML entity

  Depend output specific options:
    --depend-target=DEPEND_TARGET
                        Makefile rule target
    --depend-no-submodules
                        Do not generate dependencies for included submodules
    --depend-from-submodules
                        Generate dependencies from included submodules
    --depend-recurse    Generate dependencies to all imports, recursively
    --depend-extension=DEPEND_EXTENSION
                        YANG module file name extension
    --depend-include-path
                        Include file path in the prerequisites
    --depend-ignore-module=DEPEND_IGNORE
                        (sub)module to ignore in the prerequisites.  This
                        option can be given multiple times.

  JSTree output specific options:
    --jstree-no-path    Do not include paths to make
                        page less wide

  OmniGraffle output specific options:
    --omni-path=OMNI_TREE_PATH
                        Subtree to print

  Sample-xml-skeleton output specific options:
    --sample-xml-skeleton-doctype=DOCTYPE
                        Type of sample XML document (data or config).
    --sample-xml-skeleton-defaults
                        Insert leafs with defaults values.
    --sample-xml-skeleton-annotations
                        Add annotations as XML comments.
    --sample-xml-skeleton-path=SAMPLE_PATH
                        Subtree to print

  Tree output specific options:
    --tree-help         Print help on tree symbols and exit
    --tree-depth=TREE_DEPTH
                        Number of levels to print
    --tree-line-length=TREE_LINE_LENGTH
                        Maximum line length
    --tree-path=TREE_PATH
                        Subtree to print
    --tree-print-groupings
                        Print groupings

  UML specific options:
    --uml-classes-only  Generate UML with classes only, no attributes
    --uml-split-pages=UML_PAGES_LAYOUT
                        Generate UML output split into pages (separate .png
                        files), NxN, example 2x2
    --uml-output-directory=UML_OUTPUTDIR
                        Put generated <modulename>.png or <title>.png file(s)
                        in OUTPUTDIR (default img/)
    --uml-title=UML_TITLE
                        Set the title of the generated UML, including the
                        output file name
    --uml-header=UML_HEADER
                        Set the page header of the generated UML
    --uml-footer=UML_FOOTER
                        Set the page footer of the generated UML
    --uml-long-identifiers
                        Use the full schema identifiers for UML class names.
    --uml-inline-groupings
                        Inline groupings where they are used.
    --uml-inline-augments
                        Inline groupings where they are used.
    --uml-description   Include description of structural nodes in diagram.
    --uml-no=UML_NO     Suppress parts of the diagram.  Valid suppress values
                        are: module, uses, leafref, identity, identityref,
                        typedef, import, annotation, circles, stereotypes.
                        Annotations suppresses YANG constructs represented as
                        annotations such as config statements for containers
                        and module info. Module suppresses module box around
                        the diagram and module information.  Example --uml-
                        no=circles,stereotypes,typedef,import
    --uml-truncate=UML_TRUNCATE
                        Leafref attributes and augment elements can have long
                        paths making the classes too wide.  This option will
                        only show the tail of the path.  Example --uml-
                        truncate=augment,leafref
    --uml-max-enums=UML_MAX_ENUMS
                        The maximum number of enumerated values being rendered
    --uml-filter        Generate filter file, comment out lines with '-' and
                        use with option '--filter-file' to filter the UML
                        diagram
    --uml-filter-file=UML_FILTER_FILE
                        NOT IMPLEMENTED: Only paths in the filter file will be
                        included in the diagram
```

For example, you can run the pyang linter on our model to see how we can improve it! If you are unfamiliar with a Linter, it is a programmign tool that sniffs your code for 'code smells' and best practices. Then tells you what needs fixing for your code to be inline with best-practices.

Take a look:

```
BRANBLAC-M-W0WN:BGL Training branblac$ pyang switches.yang --lint
switches.yang:1: warning: RFC 6087: 4.1: no module name prefix string used
switches.yang:1: error: RFC 6087: 4.7: statement "module" must have a "contact" substatement
switches.yang:1: error: RFC 6087: 4.7: statement "module" must have a "organization" substatement
switches.yang:1: error: RFC 6087: 4.7: statement "module" must have a "description" substatement
switches.yang:1: error: RFC 6087: 4.7: statement "module" must have a "revision" substatement
switches.yang:5: error: RFC 6087: 4.12: statement "list" must have a "description" substatement
switches.yang:9: error: RFC 6087: 4.12: statement "leaf" must have a "description" substatement
switches.yang:11: warning: RFC 6087: 4.10,4.12: statement "enum" should have a "description" substatement
switches.yang:12: warning: RFC 6087: 4.10,4.12: statement "enum" should have a "description" substatement
switches.yang:13: warning: RFC 6087: 4.10,4.12: statement "enum" should have a "description" substatement
switches.yang:14: warning: RFC 6087: 4.10,4.12: statement "enum" should have a "description" substatement
switches.yang:18: error: RFC 6087: 4.12: statement "leaf" must have a "description" substatement
switches.yang:22: error: RFC 6087: 4.12: statement "leaf" must have a "description" substatement
switches.yang:26: error: RFC 6087: 4.12: statement "list" must have a "description" substatement
switches.yang:29: error: RFC 6087: 4.12: statement "leaf" must have a "description" substatement
switches.yang:31: warning: RFC 6087: 4.10,4.12: statement "enum" should have a "description" substatement
switches.yang:32: warning: RFC 6087: 4.10,4.12: statement "enum" should have a "description" substatement
switches.yang:33: warning: RFC 6087: 4.10,4.12: statement "enum" should have a "description" substatement
switches.yang:37: error: RFC 6087: 4.12: statement "leaf" must have a "description" substatement
switches.yang:44: error: RFC 6087: 4.12: statement "leaf" must have a "description" substatement
```

This tells us, that we can improve our code by adding 'description' substatements to our model nodes/attributes so that others can have a better idea of what they represent! along with adding contact info to the module its self.

Lets update some of these (replace with your name, email etc.):
```
module switches {
  namespace "http://example.com/switches";
  prefix switches;

  organization "Cisco Systems";
  contact "branblac@cisco.com";
  description "Module to Model switches. Lab for Cisco System IT NSO Training.";
  revision 2017-10-01 {
    description
      "Initial revision.";
    reference
      "RFC 7317: A YANG Data Model for System Management";
  }
  ...

```

Now if we re-run the linter, we have removed some out our code smells and are ready to tackle the rest!

```
BRANBLAC-M-W0WN:BGL Training branblac$ pyang switches.yang --lint
switches.yang:1: warning: RFC 6087: 4.1: no module name prefix string used
switches.yang:15: error: RFC 6087: 4.12: statement "list" must have a "description" substatement
switches.yang:19: error: RFC 6087: 4.12: statement "leaf" must have a "description" substatement
switches.yang:21: warning: RFC 6087: 4.10,4.12: statement "enum" should have a "description" substatement
switches.yang:22: warning: RFC 6087: 4.10,4.12: statement "enum" should have a "description" substatement
switches.yang:23: warning: RFC 6087: 4.10,4.12: statement "enum" should have a "description" substatement
switches.yang:24: warning: RFC 6087: 4.10,4.12: statement "enum" should have a "description" substatement
switches.yang:28: error: RFC 6087: 4.12: statement "leaf" must have a "description" substatement
switches.yang:32: error: RFC 6087: 4.12: statement "leaf" must have a "description" substatement
switches.yang:36: error: RFC 6087: 4.12: statement "list" must have a "description" substatement
switches.yang:39: error: RFC 6087: 4.12: statement "leaf" must have a "description" substatement
switches.yang:41: warning: RFC 6087: 4.10,4.12: statement "enum" should have a "description" substatement
switches.yang:42: warning: RFC 6087: 4.10,4.12: statement "enum" should have a "description" substatement
switches.yang:43: warning: RFC 6087: 4.10,4.12: statement "enum" should have a "description" substatement
switches.yang:47: error: RFC 6087: 4.12: statement "leaf" must have a "description" substatement
switches.yang:54: error: RFC 6087: 4.12: statement "leaf" must have a "description" substatement
```

Lets tackle the the first and a trickier one, then you can finish the rest:
```
list Switches {
  key Model_Number;
  description "Model that represents generic switches across manufacturers";
  ...
```
Then for the enum description statements:
```
leaf Manufacturer {
  type enumeration {
    enum 'Cisco' {
        description "Cisco Systems, cisco.com";
    }
    enum 'Juniper' {
        description "Juniper Networks, juniper.com";
    }
    enum 'Arista' {
        description "Arista Networks, arista.com";
    }
    enum 'HP' {
        description "Hewlitt Packard, hp.com";
    }
  }
  description "Manufacturer of the switch";
}
```

Finally, after adding descriptions our linter returns clean (we can ignore the error presented):
```
BRANBLAC-M-W0WN:BGL Training branblac$ pyang switches.yang --lint
switches.yang:1: warning: RFC 6087: 4.1: no module name prefix string used
```

And were done!

## Recap

In recap we:
1. Abstracted Switches into a data model
2. Defined constraints and types for the data model
3. Defined the data model in YANG
4. Linted our code for smells
5. Fixed code smells for a clean complete YANG model.
