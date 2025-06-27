import json
from time import sleep
from termcolor import colored
import os

def_config_version = 1.6

class Config_Manager():
    
    def creator():
        default_config = {
            "version": def_config_version,
            "proxies": True,
            "checkForUpdates": True,
            "oneTimeDownload": True,
            "advancedMode": False,
            "ai_training": False,
            "user_credentials": {
                "e621": {
                    "apiUser": "",
                    "apiKey": ""
                },
                "e6ai": {
                    "apiUser": "",
                    "apiKey": ""
                },
                "e926": {
                    "apiUser": "",
                    "apiKey": ""
                },
                "furbooru": {
                    "apiKey": ""
                }
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
                try:
                    config = json.load(cf)
                    config_version = config["version"]
                    advanced_mode = config["advancedMode"]
                except:
                    config_version = 0
                    advanced_mode = False
            
            if advanced_mode == True:
                return config
            
            elif config_version < def_config_version and advanced_mode != True:
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
        