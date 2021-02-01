import json
import yaml
import os
import math
import requests
from datetime import datetime
# from config import ise_node, file_path, page_limit
from progress.bar import Bar
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Making sure Yaml understand how to represent a defaultdict
from collections import defaultdict
from yaml.representer import Representer

yaml.add_representer(defaultdict, Representer.represent_dict)

# read config
with open("config.yml") as file:
    config = yaml.load(file, Loader=yaml.Loader)

if not os.environ.get("ISE_NODE"):
    ise_node = config["ise_node"]
else:
    ise_node = os.environ.get("ISE_NODE")   

if not os.environ.get("ISE_PATH"):
    file_path = config["file_path"]
else:
    file_path = os.environ.get("ISE_PATH")

if not os.environ.get("ISE_PAGE_LIMIT"):
    page_limit = int(config["page_limit"])
else:
    page_limit = int(os.environ.get("ISE_PAGE_LIMIT"))

def clear_screen():
    """ Clears the terminal window """
    if os.name == "posix":
        # mac/linux
        os.system("clear")
    else:
        # windows
        os.system("cls")

def get_device_groups(device_dict):
    """
    parses the group list for a device
    and returns the device type and location.
    """

    # grab the list 
    grouplist = device_dict["NetworkDevice"]["NetworkDeviceGroupList"]

    # clean out the crap
    groups = []
    for group  in grouplist:
        group = group.split("#")
        groups.append(group)

    #extract the device type and location 
    device_type = {"device_type": "none_type"}
    location = {"location": "none_location"}
    
    for group in groups:
        if "Device Type" in group:
            device_type = {"device_type": group[-1]}
        
        if "Location" in group:
            location = {"location": group[-1]}

    # return our shiny clean dicts
    return device_type, location

def create_inventory(ise_user, ise_password):
    """
    connects to ISE, grabs all the devices, returns a nice clean dict
    of name, ip, device type and location.
    """

    # TODO break into a couple of smaller functions.
    # retrieve list of network devices
    PAGE_SIZE = 20
    url = f"https://{ise_node}:9060/ers/config/networkdevice"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    params = {
        "size": PAGE_SIZE
    }
    
    inventory = []
    breaker = 0

    # start with a dummy dict to kickstart the while loop
    result = dict({"SearchResult": {"nextPage": "dummy value"}})

    # get device total and set up progress bar
    try:
        res = requests.get(url, headers=headers, verify=False, params=params, auth=(ise_user, ise_password))
        res.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)

    result = json.loads(res.text)
    dev_count = result['SearchResult']['total']
    bar = Bar("Retrieving device list from ISE", max = math.ceil(dev_count / PAGE_SIZE ))

    # retrieve all the device IDs
    while result["SearchResult"].get("nextPage", "missing") != "missing" and breaker <= page_limit or len(inventory) == 0:
        # use the next page reference after we've retrieved the first page
        if len(inventory) >= PAGE_SIZE:
            url = result["SearchResult"]["nextPage"]["href"]

        try:
            res = requests.get(url, headers=headers, verify=False, params=params, auth=(ise_user, ise_password))
            res.raise_for_status()
        except requests.exceptions.HTTPError as err:
          raise SystemExit(err)

        result = json.loads(res.text)
        device_list = result["SearchResult"]["resources"]
        
        for device in device_list:
            device_dict = {"id": device["id"]}
            inventory.append(device_dict)
        
        # stop looping after x pages
        breaker += 1
        
        bar.next()
    bar.finish
    print("\n")  
                
    # populate dict with details about network devices
    bar = Bar('Retrieving device details from ISE', max=len(inventory))
    
    baseurl = f"https://{ise_node}:9060/ers/config/networkdevice/"
    for device in inventory:
        id = device["id"]
        url = baseurl+id
        
        try:
            res = requests.get(url, headers=headers, verify=False, params=params, auth=(ise_user, ise_password))
            res.raise_for_status()
        except requests.exceptions.HTTPError as err:
            raise SystemExit(err)

        result = json.loads(res.text)
        device["ip"] = result["NetworkDevice"]["NetworkDeviceIPList"][0]["ipaddress"]
        device["name"] = result["NetworkDevice"]["name"]
        device_type, location = get_device_groups(result)
        device.update(device_type)
        device.update(location)
        bar.next()
    bar.finish

    ######## Debugging stuff ##########
    #    
    # with open("python_dict.json", "w") as file:
    #    json.dump(inventory, file)

    return inventory

def generate_yaml(devices, filename=file_path):
    """
    pass in a device dictionary, function will
    normalize group names to ansible standards
    and output a yaml file with a site/device_type
    structure
    """
    # remove any illegal characters for Ansible groups
    illegal_chars = " -"

    for device in devices:
        for c in illegal_chars:
            if c in device["location"]:
                device["location"] = device["location"].replace(c, "_")
            
            if c in device["device_type"]:
                device["device_type"] = device["device_type"].replace(c, "_")
    
    ######## used for static testing ########
    #with open("python_dict.json", "r") as file:
    #    devices = json.load(file)
    #########################################

    def nested_default():
        return defaultdict(dict)
    
    inventory = defaultdict(dict)
    inventory["all"]["children"] = defaultdict(nested_default)

    for device in devices:
        name, ip, device_type, location = (
        device["name"], device["ip"], device["device_type"].lower(), device["location"]
        )

        inventory["all"]["children"][location]["hosts"][name] = {"ansible_host": ip}
        inventory["all"]["children"][device_type]["hosts"][name] = {"ansible_host": ip}

    print(f"\n \n **** Writing inventory to disk at location: {filename}. time: {datetime.now()} ****")

    with open(filename, "w") as file:
        yaml.dump(inventory, file)

    return 


# with open("python_dict.json", "r") as file:
#     devices = json.load(file)

# generate_yaml(devices)