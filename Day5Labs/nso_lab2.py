'''
Script for NSO Training Day 2 Lab 2

Your goal for this lab is to modify the main function so that it updates
the voice vlan rather than the data vlan.

Step 1:
    Add the hostname and int_id to the find_hierarchy() function call and run it
    to read the information associated with each piece of NSO object.

Step 2:
    Complete the find_hierarchy() function so that it prints the class type
    and attributes of the switchport object.

Step 3:
    Note that the switchport object has an attribute named "voice". This is
    to be expected, because of the command "switchport voice vlan XXX".
    Update the main function so that it updates the voice vlan rather than
    the data vlan.
'''
from __future__ import print_function
import ncs

def find_hierarchy(hostname, int_id):
    '''Find the attributes of various NSO objects.

    Args:
        hostname (str): Name of the SVL switch that you are configuring.
        int_id (str): The GigabitEthernet ID
    '''
    with ncs.maapi.single_read_trans('admin', 'python') as trans:
        root = ncs.maagic.get_root(trans)

        device = root.devices.device[hostname]
        print("device has the following name: {}".format(device))
        print("device has the hostname: {}".format(device.name))
        print("device is of the class: {}".format(device.__class__))
        print("device has the following attributes:")
        print(dir(device))
        print("\n\n")

        interface = device.config.ios__interface.GigabitEthernet[int_id]
        print("interface has the following name: {}".format(interface))
        print("interface has the ID: {}".format(interface.name))
        print("interface is of the class: {}".format(interface.__class__))
        print("interface has the following attributes:")
        print(dir(interface))
        print("\n\n")

        switchport = interface.switchport
        # Insert print statements here



        access = switchport.access
        print("access has the following name: {}".format(access))
        print("access is of the class: {}".format(access.__class__))
        print("access has the following attributes:")
        print(dir(access))
        print("\n\n")

        vlan = access.vlan
        print("vlan has the following name: {}".format(vlan))
        print("vlan is of the class: {}".format(vlan.__class__))
        print("vlan has the following attributes:")
        print(dir(access))
        print("\n\n")


def main(hostname, int_id, new_vlan=None):
    '''Connects to an SVL device and configures an interface for a new vlan.

    Args:
        hostname (str): Name of the SVL switch that you are configuring.
        int_id (str): The GigabitEthernet ID
        new_vlan (str): The new vlan that you want to change to.
    '''
    with ncs.maapi.single_write_trans('admin', 'python') as trans:
        root = ncs.maagic.get_root(trans)
        device = root.devices.device[hostname]

        interface = device.config.ios__interface.GigabitEthernet[int_id]
        print("GigabitEthernet{0} is on voice vlan {1}"
              .format(int_id, interface.switchport.access.vlan))

        if new_vlan:
            interface.switchport.access.vlan = new_vlan

            print("Applying transaction...")
            trans.apply()

            print("GigabitEthernet{0} is now on voice vlan {1}"
                  .format(int_id, interface.switchport.access.vlan))

if __name__ == "__main__":
    find_hierarchy()
