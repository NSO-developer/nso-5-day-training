'''
Script for NSO Training Day 2 Lab 5

Your goal for this lab is to learn how to retrieve operational data from NSO.

Step 1:
    Print operational data from "show cdp neighbor detail" and "dir" using the
    functions provided.

Step 2:
    Update the send_show_cdp() so that it takes in a generic parameter and
    can be used for any show command.

Step 3:
    Prove that it works by sending "show access-lists and retrieving the output."
'''
from __future__ import print_function
import ncs

def send_show_command(hostname, params):
    '''Send a show command and return results.

    Args:
        hostname (str): Name of the device.
        params (str): The part of the command after "show "

    Returns:
        (str) Data from show command.
    '''
    pass


def send_show_cdp(hostname):
    '''Send a show cdp neighbor detail and return results.

    Args:
        hostname (str): Name of the device.

    Returns:
        (str) Data from show cdp neighbor detail.
    '''
    with ncs.maapi.single_read_trans('admin', 'python') as trans:
        root = ncs.maagic.get_root(trans)
        nso_input = root.devices.device[hostname].live_status \
                    .ios_stats__exec.show.get_input()
        nso_input.args = ["cdp neighbor detail"]
        return root.devices.device[hostname].live_status \
               .ios_stats__exec.show(nso_input).result

def send_dir_command(hostname):
    '''Since it does not lead with "show", dir requires a separate function.

    Args:
        hostname (str): Name of the device.

    Returns:
        (str) Data from dir.
    '''
    with ncs.maapi.single_read_trans('admin', 'python') as trans:
        root = ncs.maagic.get_root(trans)
        nso_input = root.devices.device[hostname].live_status \
                    .ios_stats__exec.any.get_input()
        nso_input.args = ["dir"]
        return root.devices.device[hostname].live_status \
               .ios_stats__exec.any(nso_input).result

if __name__ == "__main__":
    send_show_cdp("")
