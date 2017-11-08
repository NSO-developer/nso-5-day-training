'''
Script for NSO Training Day 2 Lab 3

Your goal for this lab is to learn how to deal with sync issues and how to
programmaticaly update the device.

Step 1:
    This is the same main function as from lab 1. Run it without the new_vlan
    parameter. Confirm that the value shown is the same as that of the device.

Step 2:
    Modify the data vlan of the device to something different without using NSO.
    SSH directly to the device and configure it through the Cisco CLI. This
    is to simulate an out-of-band change.

Step 3:
    Run the main() function again. The values should not match.

Step 4:
    There is sync function already written which does the check-sync
    and updates the NSO cDB if the device is out-of-sync. Add it to the
    appropriate location in the main function.

Step 5:
    Run the updated main function and confirm that the values match.
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

def sync(hostname, device):
    '''Does a sync-from if device is not in-sync.

    Args:
        hostname (str): Name of the SVL switch that you are configuring.
        device (Maagic.ListElement): NSO device object for the given switch.
    '''
    print("Checking if device {} is in-sync...".format(hostname))
    check_sync_output = device.check_sync.request()
    print("Output of check-sync: {}".format(check_sync_output.result))

    if check_sync_output.result != "in-sync":
        print("Syncing device {}...".format(hostname))
        sync_output = device.sync_from.request()
        print("Output of sync-from: {}".format(sync_output.result))

if __name__ == "__main__":
    main()
