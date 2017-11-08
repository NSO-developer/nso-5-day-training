'''
Script for NSO Training Day 2 Lab 1

Your goal for this lab is to familiarize yourself with the syntax
of the NSO Python API by interacting with Vlan data on a SVL switch.

Step 1:
    Identify the hostname of the SVL switch that you want to configure.
    Find a GigabitEthernet interface on that given device that has
    "switchport access vlan XXX" configured. If you cannot find one, go ahead
    and configure an interface through the CLI.

Step 2:
    Go to the section under "if __name__ == "__main__":"
    For the function call to main(), input the parameters for the hostname
    and the int_id. Do not call the function with the new_vlan parameter.

Step 3:
    Does the printed vlan information match with that of the live device?

Step 4:
    Now call the main() function with the new_vlan parameter. Read the docstring
    of the main() function in order to determine the data type of new_vlan.

Step 5:
    Confirm that the interface has updated to the new_vlan value through
    the CLI.
'''
from __future__ import print_function
import ncs

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
        print("GigabitEthernet{0} is on vlan {1}"
              .format(int_id, interface.switchport.access.vlan))

        if new_vlan:
            interface.switchport.access.vlan = new_vlan

            print("Applying transaction...")
            trans.apply()

            print("GigabitEthernet{0} is now on vlan {1}"
                  .format(int_id, interface.switchport.access.vlan))

if __name__ == "__main__":
    # Example function call: main("svl290-gg07-c3850-sw5-econ.cisco.com", "1/0/17")
    main()
