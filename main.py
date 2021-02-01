#!/usr/bin/env python
import os
from getpass import getpass
from art import banner
from functions import (
    clear_screen,
    generate_yaml,
    create_inventory
)

if __name__ == "__main__":
    clear_screen()
    
    print(banner)
    print("This tool extracts all of your devices from ISE")
    print("and creates an Ansible compatible YAML inventory file\n")
    # get username and password for ISE
    ise_user = os.environ.get("ISE_USER")
    ise_password = os.environ.get("ISE_PASSWORD")

    while (not ise_user) or (not ise_password):
        print("ISE_USER AND/OR ISE_PASSWORD environment variables not found.")
        ise_user = input("Please enter a username: ")
        ise_password = getpass("Please enter a password: ")

    inventory = create_inventory(ise_user, ise_password)

    generate_yaml(inventory)


