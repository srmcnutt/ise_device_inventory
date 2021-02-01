```
   __   ___                               
| /__` |__                                
| .__/ |___                               
                                          
 __   ___         __   ___                
|  \ |__  \  / | /  ` |__                 
|__/ |___  \/  | \__, |___                
                                          
 ___     ___  __        __  ___  __   __  
|__  \_/  |  |__)  /\  /  `  |  /  \ |__) 
|___ / \  |  |  \ /~~\ \__,  |  \__/ |  \ v0.1
                                          
- by Steven McNutt, CCIE #6495. @densem0de on twitterz
```

This tool extracts all of your devices from ISE
and creates an Ansible compatible YAML inventory file

1. Housekeeping and setup
2. how to use it
3. caveats, etc.

---------------------------------------------------------------------------

1. Housekeeping and setup

before you can fire up the tool you'll need to complete this short checklist:

- enable ERS in ISE

- write down the hostname of node that's hosting the ERS api on the ERS page

- create an account with ers readonly rights

- in the config.yml, change the name of the ise_node to the address of the
    server you wrote down above.  you can also set the ISE_NODE environment variable instead.

- (optional) configure the file_path setting in config.yml or setting the ISE_PATH environment variable 

- (optional) if you have more than 1000 devices increase the page_limit in config.yml or set the ISE_PAGE_LIMIT envrionment variable

- (optional) set the ISE_USER and ISE_PASSWORD environment variables for unnatended operation such as part of a pipeline.  if you don't set these the tool will prompt for the information.

- set up your python envronment, then run 'pip install -r requirements.txt'.  This will grab the modules that the tool needs to run.  strongly recommend virtual environments for most reliable results.

---------------------------------------------------------------------------

2. how to use it.

- type:" python3 main.py". The program will connect to ISE and start downloading the
    device inventory.

- once ISE device extractor has processed the data, you'll see a "writing inventory to disk" message.
  at that point you are done.
---------------------------------------------------------------------------
3. caveats, etc.

- the tool will build an inventory with a group per location and per device type.  You can combine them in Ansible with a host pattern.  For example dc01:&routers would select all of the routers at site dc01.  Check the Ansible documentation for further details.

- ansible inventory files cannot have whitespace or dashes in group names.  The tool will replace the location and device_type
    fields that have these characters with an underbar (_).

- if you want to contribute or modify the program, there are some sample data structures in the data_ref folder to work with.

- all configurables can set as environment variables for automation use.

- no, you cannot store the username or password in the config file.

- garbage in, garbage out.  If your ISE hygiene is poor you're going to get a crappy inventory file. I know people don't 
    like having their baby called ugly but sometimes we have to embrace these awkward moments for the greater good.

