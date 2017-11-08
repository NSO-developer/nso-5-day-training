'''
Script for NSO Training Day 2 Lab 4

Your goal in this lab is to learn how to iterate through the list objects
and manipulate large sets of NSO objects.

Step 1:
    Run the main function and see the outputted data.

Step 2:
    For any GigabitEthernet interface with a "2" digit in the interface ID
    and already has an assigned vlan, change the data vlan to 2.
    For example, Gi1/0/2, Gi1/0/20, Gi2/0/1 would all be in scope to be
    modified. If the vlan is None, ignore it.

Step 3:
    Complete the audit function so that it returns a list of interface IDs
    that belong to vlan 2.
'''
from __future__ import print_function
import ncs

def main(hostname, new_vlan=None):
    '''Connects to an SVL device and changes the vlan for many interfaces.

    Args:
        hostname (str): Name of the SVL switch that you are configuring.
        new_vlan (str): The new vlan that you want to change to.
    '''
    with ncs.maapi.single_write_trans('admin', 'python') as trans:
        root = ncs.maagic.get_root(trans)
        device = root.devices.device[hostname]

        for interface in device.config.ios__interface.GigabitEthernet:
            vlan_id = interface.switchport.access.vlan
            print("GigabitEthernet{0} is on vlan {1}"
                  .format(interface.name, vlan_id))


def audit_vlan2(hostname):
    '''Return a list of all interfaces that are on vlan 2.

    Args:
        hostname (str): Name of the SVL switch that you are configuring.

    Returns:
        (list[str]): List of interface IDs that belong on vlan 2.
    '''
    pass



if __name__ == "__main__":
    main("", "2")
    #print(audit_vlan2(""))
