import ncs
import socket
"""
This File provides servel functions that give example sof executing common tasks using the NSO Maagic API
These a written for use on a local NSO instance and are intended to be used for demonstration purposes.
"""

def create_session():
    """
    This is an example of how to create a session into NSO.
    A sessions allows for reading data from NSO and executing Actions. It does not create a transaction into NSO.
    """
    with ncs.maapi.Maapi() as m:
       with ncs.maapi.Session(m, 'admin', 'python', groups=['ncsadmin']):
           root = ncs.maagic.get_root(m)

def create_transaction():
    """
    This is an example of how to create a transaction into NSO.
    We create the transaction with the ncs.maapi.single_write_trans against the ncs module
    We commit the transaction with the apply() method inside the transaction object we created above.
    """
    with ncs.maapi.single_write_trans('admin', 'python', groups=['ncsadmin']) as t:
        root = ncs.maagic.get_root(t)
        t.apply()

def navigate_config(device_name):
    """
    Example of how to understand and navigate a devices config in the python API.
    This example will show by printing the directory of differnet levels of the config
    """
    with ncs.maapi.Maapi() as m:
       with ncs.maapi.Session(m, 'admin', 'python', groups=['ncsadmin']):
           root = ncs.maagic.get_root(m)
           device_config = root.devices.device[device_name].config
           print(dir(device_config))
           print(dir(device_config.ip))
           print(dir(device_config.ip.dhcp))
           print(dir(device_config.ip.dhcp.snooping))

def change_config_hostname(device_name):
    """
    Function to change the hostname of a provided device. This is to give an example of making config changes in NSO
    We do this by:
    1. create a transaction
    2. create a device pointer by passing the device name into the NSO list of devices.
        a. This list (root.devices.device) acts much like a Python List,
           it has key value pairs with key beign the device name and value being the object for that device.
    3. Set the value of the device's config hostname by assigning the device objects config.hostname atrribute to the new value
    4. We finish by applying the transaction we have created
    """
    with ncs.maapi.single_write_trans('admin', 'python', groups=['ncsadmin']) as t:
        root = ncs.maagic.get_root(t)
        device = root.devices.device[device_name]
        device.config.hostname = "new_host_name"
        t.apply()

def delete_data(device_name):
    """
    Example of how to delete data (config or NSO) via python
    uses python del operator
    a note! If you del a pointer to a NCS object this will only delete the pointer!
    """
    with ncs.maapi.single_write_trans('admin', 'python', groups=['ncsadmin']) as t:
        root = ncs.maagic.get_root(t)
        del root.devices.device[device_name].config.hostname
        t.apply()

def create_list_item():
    """
    Example of how to add a new item into a list resource.
    In the IOS YANG model there are many instances of Lists.
    For example, adding a new VLAN would be adding a new item to a list.
    We do this by invoking the .create() method of the ncs list objects
    """
    with ncs.maapi.single_write_trans('admin', 'python', groups=['ncsadmin']) as t:
        root = ncs.maagic.get_root(t)
        root.devices.device.config.interface.vlan.create("200")
        t.apply()

def add_device(device_name):
    """
    This function takes a device hostname as an input and adds that device into NSO.
    Then does an nslookup on the hostname
    This function uses 3 seperate transactions do to sequencing and default admin-state in NSO of locked.
    First Transaction: Adds the device and IP to add the device into the cDB
    Second Transaction: adds the port and creates the device-type/ NED info and unlocks the device.
    Third Transaction: Gets ssh keys, syncs-from and southbound-locks the device.
    """
    ip_addr = socket.getaddrinfo(device_name,0,0,0,0)
    with ncs.maapi.single_write_trans('admin', 'python', groups=['ncsadmin']) as t:
        root = ncs.maagic.get_root(t)
        root.devices.device.create(device_name)
        root.devices.device[device_name].address = ip_addr[0][4][0]
        t.apply()
    with ncs.maapi.single_write_trans('admin', 'python', groups=['ncsadmin']) as t2:
        root = ncs.maagic.get_root(t2)
        root.devices.device[device_name].port = 22
        root.devices.device[device_name].device_type.cli.create()
        root.devices.device[device_name].device_type.cli.ned_id = "ios-id:cisco-ios"
        root.devices.device[device_name].device_type.cli.protocol = "ssh"
        root.devices.device[device_name].authgroup = "branblac"
        root.devices.device[device_name].state.admin_state = "unlocked"
        t2.apply()
    with ncs.maapi.single_write_trans('admin', 'python', groups=['ncsadmin']) as t3:
        root = ncs.maagic.get_root(t3)
        root.devices.device[device_name].ssh.fetch_host_keys()
        root.devices.device[device_name].sync_from()
        root.devices.device[device_name].state.admin_state = "southbound-locked"
        t3.apply()

def iterate_devices():
    """
    Example of how to loop  over devices in NSO and execute actions or changes per each device.
    Within this example we will iterate over devices and print the device name and the HW platform.
    Then per device print what extended ACL are present on the device.
        Notice how the configuration for the device is navigated via a python object
        In this case config -> ip -> access-list -> extended -> ext_named_acl
        If you thinka bout it, this object structure is very similiar to the IOS syntax and navigation
    We do this by:
    1. Creating a transaction
    2. Using a for loop over the the root.devices.device list
    3. Printing the info, print info per box
    In this example, we should have used a session! but if we desire changes we per box we would want a transaction.
    In this case, even if we changed config info, nothing would be done! Since we never apply/commit the transaction changes.
    """
    with ncs.maapi.single_write_trans('admin', 'python', groups=['ncsadmin']) as t:
        root = ncs.maagic.get_root(t)
        for box in root.devices.device:
            print(box.name,": ", box.platform.model)
            for acl in root.devices.device[box.name].config.ip.access_list.extended.ext_named_acl:
                print(acl.name)

def show_commands(command, device_name):
    """
    Use a MAAPI session via maagic api to get the results of a passed show command.
    Uses the devices name in NSO as an input parameter and the commnd ie: CDP Neighbors, ip int br.
    prints the raw text results of the command.
    We do this by:
    1. Creating a NSO session
    2. Create a pointer to our device
    3. Create an input object but calling the device.live_status.ios_stats__exec.show.get_input() emthod
    4. Pass the command function input into the input objects args variable
    5. Invoke the command by passign the input object into the device.live_status.ios_stats__exec.show() method
    6. set the output variable to the result attributw of our invoked command object above
    7.Print the output
    """
    with ncs.maapi.Maapi() as m:
       with ncs.maapi.Session(m, 'admin', 'python'):
           root = ncs.maagic.get_root(m)
           device = root.devices.device[device_name]
           input1 = device.live_status.ios_stats__exec.show.get_input()
           input1.args = [command]
           output = device.live_status.ios_stats__exec.show(input1).result
           print(output)

def clear_commands(command, device_name):
    """
    Same as above but for clearing
    """
    with ncs.maapi.Maapi() as m:
       with ncs.maapi.Session(m, 'admin', 'python'):
           root = ncs.maagic.get_root(m)
           device = root.devices.device[device_name]
           input1 = device.live_status.ios_stats__exec.clear.get_input()
           input1.args = [command]
           output = device.live_status.ios_stats__exec.clear(input1).result
           print(output)

def using_leaflists_data(device_group):
    """
    Example that shows one scenario where you will use a leaflist YANG type.
    This example iterates over the devices in a provided group the passes
    the string value from the list into root.devices.device[] to get the ip address of the device.
    """
    with ncs.maapi.single_write_trans('ncsadmin', 'python', groups=['ncsadmin'], db=ncs.RUNNING, ip='127.0.0.1', port=ncs.NCS_PORT, proto=ncs.PROTO_TCP) as trans:
        root = ncs.maagic.get_root(trans)
        group = root.devices.device_group[device_group].device_name
        for box in group:
            print type(box)
            print(root.devices.device[box].address)

def check_in_string(ip):
    """
    Single search to see if a provided IP address
    is present inside any of a devices extended ACLs.
    """
    with ncs.maapi.single_write_trans('admin', 'python', groups=['ncsadmin']) as t:
        root = ncs.maagic.get_root(t)
        for box in root.devices.device:
            for acl in root.devices.device[box.name].config.ip.access_list.extended.ext_named_acl:
                for rule in root.devices.device[box.name].config.ip.access_list.extended.ext_named_acl[acl.name].ext_access_list_rule:
                    if ip in rule.rule:
                        print(ip + "Is in acl " + str(acl))

def work_with_boolean(device_name):
    """
    Function example that shows values that are of data type boolean.
    These can be set to be True or False.

    Also showing object assignment for fun.
    """
    with ncs.maapi.single_write_trans('admin', 'python', groups=['ncsadmin']) as t:
        root = ncs.maagic.get_root(t)
        dot_one_q_config = root.devices.device[device_name].config.interface.GigabitEthernet["0/1"].dot1Q
        dot_one_q_config.vlan_id = 10
        dot_one_q_config.native = True

def check_if_interface_exists(device_name, interface_type, interface_number):
    """
    Example function to show how to check if a certain interface is on a device.

    We do this by using by if in operators and the maagic API dictionary methods.
    """
    with ncs.maapi.single_write_trans('admin', 'python', groups=['ncsadmin']) as t:
        root = ncs.maagic.get_root(t)
        device = root.devices.device[device_name]
        print type(device.interface[interface_type])
        if interface_number in device.interface[interface_type]:
            print("Interface is on the device!")
        else:
            print("Interface is not on the device!")

def print_interfaces(device_name, interface_type):
    """
    Prints each interface number on the device of the given type
    """
    with ncs.maapi.single_write_trans('admin', 'python', groups=['ncsadmin']) as t:
        root = ncs.maagic.get_root(t)
        device = root.devices.device[device_name]
        for interface in device.interface[interface_type]:
            print interface.name

#see FSM templates for many show commands here:
# https://github.com/networktocode/ntc-templates/tree/master/templates
    # username = 'ncsadmin'
    # context = 'python'
def show_command_parsed_with_fsm_template (username, context,devicename,showx,templatefile):

    try:
        with ncs.maapi.single_read_trans(username, context, [username]) as t:
            root = ncs.maagic.get_root(t)
            device = root.devices.device[devicename]
            input1 = device.live_status.ios_stats__exec.show.get_input()
            input1.args = [showx]
            showcommand = device.live_status.ios_stats__exec.show(input1).result
            print showcommand

    except :
        print "This device is not reachable"
        return 1

    filename = 'templates/'+str(templatefile)
    template = open(filename)
    fsm = textfsm.TextFSM(template)
    fsm_results = fsm.ParseText(showcommand)
    print "fsm results"
    print fsm_results
    return fsm_results

#Take FSM results and output to CSV
def resultstocsv(self,dict,filename):
    filename = str(filename)+".csv"
    with open(filename,'wb') as f:
        w = csv.writer(f)
        w.writerows(dict.items())


def getdevicelist(username, context,devicekeyword,devicehw):
    """
    from device list, filter down to ones you want based on hostname and hw type
    :param username:  Username used to login to NSO
    :param context: Context used to login to NSO
    :param devicekeyword: regex to find in hostname, like "wan" in wan-gw
    :param devicehw:
    :return: list of device names sorted alphabetically
    """
    result = []
    with ncs.maapi.single_read_trans(username, context, [ username ]) as t:
        root = ncs.maagic.get_root(t)
        devicelist = root.devices.device
        for device in devicelist:
            devicename = device.name
            hardwaretype = root.devices.device[devicename].config.ios__cached_show.version.model
            print hardwaretype
            print devicename
            try:
                if devicekeyword in devicename and devicehw in hardwaretype:
                    result.append(devicename)
                    result.sort(key=str.lower)
            except:
                continue
    return result
