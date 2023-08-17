import json
from time import sleep
from termcolor import colored
import os

def_config_version = 1.4

class Config_Manager():
    
    def creator():
        default_config = {
            "version": def_config_version,
            "proxies": True,
            "checkForUpdates": True,
            "oneTimeDownload": True,
            "user_credentials": {
                "e621": {
                    "apiUser": "",
                    "apiKey": ""
                },
                "e926": {
                    "apiUser": "",
                    "apiKey": ""
                },
                "furbooru": {
                    "apiKey": ""
                },
                "github": {
                    "apiKey": ""
                },
            },
            "blacklisted_tags": [
                "example1",
                "example2"
            ],
            "blacklisted_formats": [
                "example1",
                "example2"
            ]
        }
        with open("config.json", "w") as cf:
            json.dump(default_config, cf, indent=6)
        return 1
        # 1 stands for successful
    
    def reader():
        if os.path.exists("config.json"):
            with open("config.json", "r") as cf:
                config = json.load(cf)
                config_version = config["version"]
                
            if config_version < def_config_version:
                print(colored("You are using an outdated config version! Old one is backed up. Please reconfigure the new one.", "green"))
                if os.path.exists("old_config.json"):
                    os.remove("old_config.json")
                    os.rename("config.json", "old_config.json")
                else:
                    os.rename("config.json", "old_config.json")
                Config_Manager.creator()
                sleep(7)
                exit(0)
            return config
        else:
            return 0
        # 0 means unsuccessful
         
    def compare():
        # TODO: Add working config compare method instead of simple config version number
        print("how in the hell did you even manage to get this printed?")
                        
    def updater():
        # TODO: Add working config updater
        print("how in the hell did you even manage to get this printed?")
        